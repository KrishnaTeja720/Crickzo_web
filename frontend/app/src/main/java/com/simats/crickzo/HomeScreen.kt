package com.simats.crickzo

import android.content.Context
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.KeyboardArrowRight
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.AddCircle
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.History
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.outlined.Home
import androidx.compose.material.icons.outlined.Person
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.simats.crickzo.ui.theme.GrayText
import kotlinx.coroutines.launch

@Composable
fun HomeScreen(
    userName: String,
    userEmail: String,
    userId: Int,
    onUpdateProfile: (String, String) -> Unit,
    onLogout: () -> Unit
) {
    var currentScreen by remember { mutableStateOf("Home") }
    val coroutineScope = rememberCoroutineScope()
    
    // States for forgot password flow
    var forgotPasswordEmail by remember { mutableStateOf("") }
    var resetOtp by remember { mutableStateOf("") }
    
    // States for match creation flow
    val currentMatchId = remember { mutableIntStateOf(0) }
    val teamAName = remember { mutableStateOf("") }
    val teamBName = remember { mutableStateOf("") }
    
    // State for MyMatches tab navigation
    var myMatchesInitialTab by remember { mutableStateOf("Live") }
    
    // API Data Lists
    val liveMatchesList = remember { mutableStateListOf<LiveMatchData>() }
    val createdMatches = remember { mutableStateListOf<CreatedMatch>() }
    val completedMatchesList = remember { mutableStateListOf<CompletedMatchInfo>() }
    
    var selectedMatchForScoring by remember { mutableStateOf<CreatedMatch?>(null) }
    var selectedLiveMatch by remember { mutableStateOf<LiveMatchData?>(null) }
    var selectedCompletedMatch by remember { mutableStateOf<CompletedMatchInfo?>(null) }
    var isRefreshing by remember { mutableStateOf(false) }

    fun refreshMatches() {
        if (isRefreshing) return
        isRefreshing = true
        coroutineScope.launch {
            try {
                val response = RetrofitClient.apiService.getLiveMatches(userId)
                if (response.isSuccessful) {
                    liveMatchesList.clear()
                    createdMatches.clear()
                    response.body()?.let { matches ->
                        liveMatchesList.addAll(matches)
                        matches.forEach { liveMatch ->
                            val matchIdStr = liveMatch.matchId.toString()
                            val playersA = mutableListOf<String>()
                            val playersB = mutableListOf<String>()

                            val playersRes = RetrofitClient.apiService.getMatchPlayers(matchIdStr)
                            if (playersRes.isSuccessful) {
                                playersRes.body()?.forEach { player ->
                                    if (player.teamName == "TeamA") playersA.add(player.playerName)
                                    else if (player.teamName == "TeamB") playersB.add(player.playerName)
                                }
                            }

                            val matchStatus = if (liveMatch.runs > 0 || liveMatch.wickets > 0 || liveMatch.overs > 0) "LIVE" else "UPCOMING"
                            createdMatches.add(CreatedMatch(
                                id = matchIdStr,
                                teamA = liveMatch.teamA ?: "Team A",
                                teamB = liveMatch.teamB ?: "Team B",
                                teamAPlayers = playersA,
                                teamBPlayers = playersB,
                                status = matchStatus,
                                location = liveMatch.venue ?: "Local Ground",
                                striker = "",
                                nonStriker = "",
                                bowler = ""
                            ))
                        }
                    }
                }
                
                val compResponse = RetrofitClient.apiService.getCompletedMatches(userId)
                if (compResponse.isSuccessful) {
                    completedMatchesList.clear()
                    compResponse.body()?.let { completedMatchesList.addAll(it) }
                }
            } catch (e: Exception) {
                e.printStackTrace()
            } finally {
                isRefreshing = false
            }
        }
    }

    LaunchedEffect(Unit) {
        refreshMatches()
    }

    val noBottomBarScreens = remember {
        setOf(
            "ForgotPassword", "VerifyOtp", "ResetPassword", "CreateMatch", "AddPlayers",
            "Scoring", "MyMatches", "LiveMatches", "CompletedMatches", "Predictions", "CompletedMatchDetail"
        )
    }
    val hideBottomBar = currentScreen in noBottomBarScreens

    Scaffold(
        bottomBar = {
            if (!hideBottomBar) {
                CrickzoBottomBar(
                    selectedItem = if (currentScreen == "AccountSettings") "Profile" else currentScreen,
                    onItemSelected = { screen ->
                        currentScreen = if (screen == "Add Match") "CreateMatch" else screen
                    }
                )
            }
        }
    ) { innerPadding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(if (hideBottomBar) PaddingValues(0.dp) else innerPadding)
        ) {
            if (isRefreshing) {
                LinearProgressIndicator(
                    modifier = Modifier.fillMaxWidth().align(Alignment.TopCenter),
                    color = Color(0xFF1E40AF)
                )
            }
            when (currentScreen) {
                "Home" -> HomeContent(
                    userName = userName,
                    liveMatches = liveMatchesList,
                    userCreatedMatchesCount = createdMatches.size,
                    onCreateMatchClick = { currentScreen = "CreateMatch" },
                    onMyMatchesClick = { 
                        myMatchesInitialTab = "Live"
                        currentScreen = "MyMatches" 
                    },
                    onLiveMatchesClick = { 
                        myMatchesInitialTab = "Live"
                        currentScreen = "MyMatches" 
                    },
                    onCompletedMatchesClick = { currentScreen = "CompletedMatches" },
                    onMenuAction = { action ->
                        when (action) {
                            "Profile" -> currentScreen = "Profile"
                            "AccountSettings" -> currentScreen = "AccountSettings"
                            "Logout" -> onLogout()
                        }
                    }
                )
                "ForgotPassword" -> {
                    ForgotPasswordScreen(
                        onBackToLogin = { currentScreen = "AccountSettings" },
                        onCodeSent = { email ->
                            forgotPasswordEmail = email
                            currentScreen = "VerifyOtp"
                        }
                    )
                }
                "VerifyOtp" -> {
                    VerifyOtpScreen(
                        email = forgotPasswordEmail,
                        subtitle = "Password Recovery",
                        onBack = { currentScreen = "ForgotPassword" },
                        onVerifySuccess = { otp ->
                            resetOtp = otp
                            currentScreen = "ResetPassword"
                        }
                    )
                }
                "ResetPassword" -> {
                    ResetPasswordScreen(
                        email = forgotPasswordEmail,
                        otp = resetOtp,
                        onBack = { currentScreen = "VerifyOtp" },
                        onResetSuccess = {
                            currentScreen = "AccountSettings"
                        }
                    )
                }
                "CompletedMatches" -> {
                    CompletedMatchesScreen(
                        userId = userId,
                        matches = completedMatchesList,
                        onBack = { currentScreen = "Home" }
                    )
                }
                "CompletedMatchDetail" -> {
                    selectedCompletedMatch?.let { match ->
                        CompletedMatchDetail(
                            match = match,
                            onBack = { currentScreen = "MyMatches" }
                        )
                    }
                }
                "LiveMatches" -> {
                    LiveMatchesScreen(
                        userId = userId,
                        onBack = { currentScreen = "Home" },
                        onUpdateScore = { match ->
                            selectedMatchForScoring = null
                            selectedLiveMatch = match
                            currentScreen = "Scoring"
                        },
                        onViewPredictions = { match ->
                            selectedLiveMatch = match
                            currentScreen = "Predictions"
                        }
                    )
                }
                "Predictions" -> {
                    val match = selectedLiveMatch
                    PredictionsScreen(
                        match = match,
                        teamA = match?.teamA ?: "Team A",
                        teamB = match?.teamB ?: "Team B",
                        onBack = { currentScreen = "LiveMatches" }
                    )
                }
                "MyMatches" -> {
                    MyMatchesScreen(
                        matches = createdMatches,
                        completedMatches = completedMatchesList,
                        initialTab = myMatchesInitialTab,
                        onBack = { 
                            refreshMatches()
                            currentScreen = "Home" 
                        },
                        onScoreMatch = { match ->
                            selectedMatchForScoring = match
                            selectedLiveMatch = null
                            currentScreen = "Scoring"
                        },
                        onCompletedMatchClick = { match ->
                            selectedCompletedMatch = match
                            currentScreen = "CompletedMatchDetail"
                        },
                        onAddMatch = { currentScreen = "CreateMatch" }
                    )
                }
                "CreateMatch" -> {
                    CreateMatchScreen(
                        onBack = { currentScreen = "Home" },
                        onContinue = { id, a, b -> 
                            currentMatchId.intValue = id
                            teamAName.value = a
                            teamBName.value = b
                            currentScreen = "AddPlayers" 
                        }
                    )
                }
                "AddPlayers" -> {
                    AddPlayersScreen(
                        matchId = currentMatchId.intValue,
                        teamAName = teamAName.value,
                        teamBName = teamBName.value,
                        onBack = { currentScreen = "CreateMatch" },
                        onStartMatch = { playersA, playersB, striker, nonStriker, bowler ->
                            val newMatch = CreatedMatch(
                                id = currentMatchId.intValue.toString(),
                                teamA = teamAName.value,
                                teamB = teamBName.value,
                                teamAPlayers = playersA,
                                teamBPlayers = playersB,
                                striker = striker,
                                nonStriker = nonStriker,
                                bowler = bowler,
                                status = "UPCOMING",
                                location = "Local Ground"
                            )
                            createdMatches.add(newMatch)
                            selectedMatchForScoring = newMatch
                            selectedLiveMatch = null
                            currentScreen = "Scoring"
                        }
                    )
                }
                "Scoring" -> {
                    val scoringMatch = selectedMatchForScoring
                    val scoringLiveMatch = selectedLiveMatch
                    
                    val finalTeamAPlayers = remember(scoringMatch, scoringLiveMatch) {
                        mutableStateListOf<String>().apply {
                            if (scoringMatch != null) {
                                addAll(scoringMatch.teamAPlayers)
                            }
                        }
                    }
                    val finalTeamBPlayers = remember(scoringMatch, scoringLiveMatch) {
                        mutableStateListOf<String>().apply {
                            if (scoringMatch != null) {
                                addAll(scoringMatch.teamBPlayers)
                            }
                        }
                    }

                    LaunchedEffect(scoringLiveMatch) {
                        if (scoringLiveMatch != null && scoringMatch == null) {
                            val matchIdStr = scoringLiveMatch.matchId.toString()
                            val res = RetrofitClient.apiService.getMatchPlayers(matchIdStr)
                            if (res.isSuccessful) {
                                val players = res.body() ?: emptyList()
                                finalTeamAPlayers.clear()
                                finalTeamBPlayers.clear()
                                players.forEach { p ->
                                    if (p.teamName == "TeamA") finalTeamAPlayers.add(p.playerName)
                                    else if (p.teamName == "TeamB") finalTeamBPlayers.add(p.playerName)
                                }
                            }
                        }
                    }

                    ScoringScreen(
                        matchId = scoringMatch?.id ?: scoringLiveMatch?.matchId?.toString() ?: "0",
                        teamAName = scoringMatch?.teamA ?: scoringLiveMatch?.teamA ?: "Team A",
                        teamBName = scoringMatch?.teamB ?: scoringLiveMatch?.teamB ?: "Team B",
                        teamAPlayers = finalTeamAPlayers,
                        teamBPlayers = finalTeamBPlayers,
                        initialStriker = scoringMatch?.striker ?: "",
                        initialNonStriker = scoringMatch?.nonStriker ?: "",
                        initialBowler = scoringMatch?.bowler ?: "",
                        onBack = { 
                            refreshMatches()
                            currentScreen = "Home" 
                        },
                        onMatchComplete = { completedInfo ->
                            completedMatchesList.add(completedInfo)
                            currentScreen = "Home"
                        }
                    )
                }
                "Profile" -> {
                    AccountSettingsScreen(
                        userId = userId,
                        initialName = userName,
                        initialEmail = userEmail,
                        onBack = { currentScreen = "Home" },
                        onSave = onUpdateProfile,
                        onLogout = onLogout,
                        onForgotPasswordClick = { currentScreen = "ForgotPassword" }
                    )
                }
                "AccountSettings" -> {
                    AccountSettingsScreen(
                        userId = userId,
                        initialName = userName,
                        initialEmail = userEmail,
                        onBack = { currentScreen = "Home" },
                        onSave = onUpdateProfile,
                        onLogout = onLogout,
                        onForgotPasswordClick = { currentScreen = "ForgotPassword" }
                    )
                }
            }
        }
    }
}

@Composable
fun CrickzoBottomBar(selectedItem: String, onItemSelected: (String) -> Unit) {
    NavigationBar(
        containerColor = Color.White,
        tonalElevation = 8.dp
    ) {
        NavigationBarItem(
            icon = { Icon(if (selectedItem == "Home") Icons.Filled.Home else Icons.Outlined.Home, "Home") },
            label = { Text("Home") },
            selected = selectedItem == "Home",
            onClick = { onItemSelected("Home") },
            colors = NavigationBarItemDefaults.colors(
                selectedIconColor = Color(0xFF1E40AF),
                unselectedIconColor = Color.Gray,
                selectedTextColor = Color(0xFF1E40AF),
                indicatorColor = Color(0xFFEFF6FF)
            )
        )
        NavigationBarItem(
            icon = { Icon(Icons.Default.AddCircle, "Add Match") },
            label = { Text("Add Match") },
            selected = false,
            onClick = { onItemSelected("Add Match") },
            colors = NavigationBarItemDefaults.colors(
                unselectedIconColor = Color(0xFF1E40AF),
                unselectedTextColor = Color(0xFF1E40AF)
            )
        )
        NavigationBarItem(
            icon = { Icon(if (selectedItem == "Profile") Icons.Filled.Person else Icons.Outlined.Person, "Profile") },
            label = { Text("Profile") },
            selected = selectedItem == "Profile",
            onClick = { onItemSelected("Profile") },
            colors = NavigationBarItemDefaults.colors(
                selectedIconColor = Color(0xFF1E40AF),
                unselectedIconColor = Color.Gray,
                selectedTextColor = Color(0xFF1E40AF),
                indicatorColor = Color(0xFFEFF6FF)
            )
        )
    }
}

@Composable
fun HomeContent(
    userName: String,
    liveMatches: List<LiveMatchData>,
    userCreatedMatchesCount: Int,
    onCreateMatchClick: () -> Unit,
    onMyMatchesClick: () -> Unit,
    onLiveMatchesClick: () -> Unit,
    onCompletedMatchesClick: () -> Unit,
    onMenuAction: (String) -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFFF8FAFC))
            .verticalScroll(rememberScrollState())
    ) {
        // Header
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .background(
                    brush = Brush.verticalGradient(
                        colors = listOf(Color(0xFF1E40AF), Color(0xFF2563EB))
                    )
                )
                .padding(24.dp)
        ) {
            Column {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text("Welcome back,", color = Color.White.copy(alpha = 0.8f), fontSize = 14.sp)
                        Text(userName, color = Color.White, fontSize = 24.sp, fontWeight = FontWeight.Bold)
                    }
                    IconButton(
                        onClick = { onMenuAction("AccountSettings") },
                        modifier = Modifier.background(Color.White.copy(alpha = 0.2f), CircleShape)
                    ) {
                        Icon(Icons.Default.Person, null, tint = Color.White)
                    }
                }
            }
        }

        Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(20.dp)) {
            // Live Matches Row
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text("Live Matches", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = Color(0xFF1E293B))
                Text(
                    "View All",
                    color = Color(0xFF3B82F6),
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Medium,
                    modifier = Modifier.clickable { onLiveMatchesClick() }
                )
            }

            if (liveMatches.isEmpty()) {
                Surface(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(16.dp),
                    color = Color.White,
                    border = CardDefaults.outlinedCardBorder()
                ) {
                    Box(modifier = Modifier.padding(32.dp), contentAlignment = Alignment.Center) {
                        Text("No live matches at the moment", color = GrayText, fontSize = 14.sp)
                    }
                }
            } else {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    liveMatches.take(2).forEach { match ->
                        MatchMiniCard(match, Modifier.weight(1f))
                    }
                }
            }

            // Quick Actions
            Text("Quick Actions", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = Color(0xFF1E293B))
            
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                QuickActionCard(
                    title = "New Match",
                    subtitle = "Start scoring",
                    icon = Icons.Default.Add,
                    color = Color(0xFF3B82F6),
                    modifier = Modifier.weight(1f),
                    onClick = onCreateMatchClick
                )
                QuickActionCard(
                    title = "My Matches",
                    subtitle = "$userCreatedMatchesCount matches",
                    icon = Icons.Default.History,
                    color = Color(0xFF10B981),
                    modifier = Modifier.weight(1f),
                    onClick = onMyMatchesClick
                )
            }

            // Completed Matches Section
            Surface(
                modifier = Modifier.fillMaxWidth().clickable { onCompletedMatchesClick() },
                shape = RoundedCornerShape(16.dp),
                color = Color.White,
                border = CardDefaults.outlinedCardBorder()
            ) {
                Row(
                    modifier = Modifier.padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    Box(
                        modifier = Modifier
                            .size(48.dp)
                            .background(Color(0xFFF1F5F9), CircleShape),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(Icons.Default.CheckCircle, null, tint = Color(0xFF64748B))
                    }
                    Column(modifier = Modifier.weight(1f)) {
                        Text("Completed Matches", fontWeight = FontWeight.Bold, color = Color(0xFF1E293B))
                        Text("View match history and results", fontSize = 12.sp, color = GrayText)
                    }
                    Icon(Icons.AutoMirrored.Filled.KeyboardArrowRight, null, tint = Color(0xFF94A3B8))
                }
            }
        }
    }
}

@Composable
fun MatchMiniCard(match: LiveMatchData, modifier: Modifier) {
    Surface(
        modifier = modifier,
        shape = RoundedCornerShape(16.dp),
        color = Color.White,
        border = CardDefaults.outlinedCardBorder()
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Box(modifier = Modifier.size(8.dp).background(Color.Red, CircleShape))
                Spacer(Modifier.width(6.dp))
                Text("LIVE", color = Color.Red, fontSize = 10.sp, fontWeight = FontWeight.Bold)
            }
            Spacer(Modifier.height(8.dp))
            Text("${match.teamA} vs ${match.teamB}", fontSize = 12.sp, fontWeight = FontWeight.Bold, maxLines = 1)
            Text("${match.runs}/${match.wickets}", fontSize = 18.sp, fontWeight = FontWeight.ExtraBold, color = Color(0xFF1E40AF))
            Text("${match.overs} Overs", fontSize = 10.sp, color = GrayText)
        }
    }
}

@Composable
fun QuickActionCard(title: String, subtitle: String, icon: ImageVector, color: Color, modifier: Modifier, onClick: () -> Unit) {
    Surface(
        modifier = modifier.clickable { onClick() },
        shape = RoundedCornerShape(16.dp),
        color = color.copy(alpha = 0.1f),
        border = CardDefaults.outlinedCardBorder()
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Icon(icon, null, tint = color)
            Spacer(Modifier.height(12.dp))
            Text(title, fontWeight = FontWeight.Bold, color = Color(0xFF1E293B))
            Text(subtitle, fontSize = 12.sp, color = GrayText)
        }
    }
}
