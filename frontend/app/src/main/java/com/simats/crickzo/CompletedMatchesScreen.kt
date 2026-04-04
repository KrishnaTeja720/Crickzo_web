package com.simats.crickzo

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.launch
import java.util.Locale

@Composable
fun CompletedMatchesScreen(
    userId: Int,
    matches: List<CompletedMatchInfo> = listOf(),
    onBack: () -> Unit
) {
    val coroutineScope = rememberCoroutineScope()
    var completedMatches by remember { mutableStateOf(matches) }
    var isLoading by remember { mutableStateOf(matches.isEmpty()) }
    var selectedMatch by remember { mutableStateOf<CompletedMatchInfo?>(null) }

    LaunchedEffect(Unit) {
        if (matches.isEmpty()) {
            coroutineScope.launch {
                try {
                    val response = RetrofitClient.apiService.getCompletedMatches(userId)
                    if (response.isSuccessful) {
                        completedMatches = response.body() ?: listOf()
                    }
                } catch (e: Exception) {
                    e.printStackTrace()
                } finally {
                    isLoading = false
                }
            }
        }
    }

    if (selectedMatch == null) {
        CompletedMatchesList(
            matches = completedMatches,
            isLoading = isLoading,
            onBack = onBack,
            onMatchClick = { selectedMatch = it }
        )
    } else {
        CompletedMatchDetail(
            match = selectedMatch!!,
            onBack = { selectedMatch = null }
        )
    }
}

@Composable
fun CompletedMatchesList(
    matches: List<CompletedMatchInfo>,
    isLoading: Boolean,
    onBack: () -> Unit,
    onMatchClick: (CompletedMatchInfo) -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFFF8FAFC))
    ) {
        // Header
        Surface(
            modifier = Modifier.fillMaxWidth(),
            color = Color(0xFF1E40AF)
        ) {
            Row(
                modifier = Modifier
                    .padding(top = 48.dp, bottom = 16.dp, start = 8.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                IconButton(onClick = onBack) {
                    Icon(Icons.AutoMirrored.Filled.ArrowBack, "Back", tint = Color.White)
                }
                Text(
                    text = "Completed Matches",
                    color = Color.White,
                    fontSize = 20.sp,
                    fontWeight = FontWeight.Bold
                )
            }
        }

        if (isLoading) {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator(color = Color(0xFF1E40AF))
            }
        } else if (matches.isEmpty()) {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                Text(text = "No completed matches found", color = Color(0xFF64748B))
            }
        } else {
            LazyColumn(
                modifier = Modifier.fillMaxSize(),
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                items(matches) { match ->
                    CompletedMatchCard(match = match, onClick = { onMatchClick(match) })
                }
            }
        }
    }
}

@Composable
fun CompletedMatchCard(match: CompletedMatchInfo, onClick: () -> Unit) {
    var matchWithScores by remember { mutableStateOf(match) }
    
    // Fetch scores if they are missing in the summary list
    LaunchedEffect(match.matchId) {
        if (match.teamARuns == 0 && match.teamBRuns == 0) {
            try {
                val scoreA = RetrofitClient.apiService.getScoreboard(match.matchId.toString(), 1)
                val scoreB = RetrofitClient.apiService.getScoreboard(match.matchId.toString(), 2)
                
                if (scoreA.isSuccessful || scoreB.isSuccessful) {
                    matchWithScores = matchWithScores.copy(
                        teamARuns = scoreA.body()?.runs ?: match.teamARuns,
                        teamAWickets = scoreA.body()?.wickets ?: match.teamAWickets,
                        teamAOvers = scoreA.body()?.overs ?: match.teamAOvers,
                        teamBRuns = scoreB.body()?.runs ?: match.teamBRuns,
                        teamBWickets = scoreB.body()?.wickets ?: match.teamBWickets,
                        teamBOvers = scoreB.body()?.overs ?: match.teamBOvers
                    )
                }
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    val oversA = String.format(Locale.US, "%.1f", matchWithScores.teamAOvers)
    val oversB = String.format(Locale.US, "%.1f", matchWithScores.teamBOvers)

    val teamAScore = "${matchWithScores.teamARuns}/${matchWithScores.teamAWickets} ($oversA)"
    val teamBScore = "${matchWithScores.teamBRuns}/${matchWithScores.teamBWickets} ($oversB)"
    
    val isTeamAWinner = match.winner?.trim().equals(match.teamA?.trim(), ignoreCase = true)
    val isTeamBWinner = match.winner?.trim().equals(match.teamB?.trim(), ignoreCase = true)

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        border = BorderStroke(1.dp, Color(0xFFE2E8F0))
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(text = "Match Completed", color = Color(0xFF64748B), fontSize = 12.sp)
                Surface(color = Color(0xFFF1F5F9), shape = RoundedCornerShape(4.dp)) {
                    Text(
                        text = "T20", 
                        modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp), 
                        color = Color(0xFF1E40AF), 
                        fontSize = 10.sp, 
                        fontWeight = FontWeight.Bold
                    )
                }
            }
            
            Spacer(Modifier.height(12.dp))

            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Column(modifier = Modifier.weight(1f)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(
                            text = match.teamA ?: "Unknown", 
                            fontWeight = if (isTeamAWinner) FontWeight.ExtraBold else FontWeight.Bold, 
                            fontSize = 15.sp,
                            color = if (isTeamAWinner) Color(0xFF1E40AF) else Color.Unspecified
                        )
                        if (isTeamAWinner) {
                            Spacer(Modifier.width(4.dp))
                            Icon(Icons.Default.EmojiEvents, null, tint = Color(0xFFD97706), modifier = Modifier.size(14.dp))
                        }
                    }
                    Text(text = teamAScore, color = Color(0xFF64748B), fontSize = 13.sp)
                }
                
                Text(
                    text = "VS", 
                    modifier = Modifier.padding(horizontal = 8.dp), 
                    color = Color(0xFFCBD5E1), 
                    fontSize = 12.sp, 
                    fontWeight = FontWeight.Bold
                )

                Column(modifier = Modifier.weight(1f), horizontalAlignment = Alignment.End) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        if (isTeamBWinner) {
                            Icon(Icons.Default.EmojiEvents, null, tint = Color(0xFFD97706), modifier = Modifier.size(14.dp))
                            Spacer(Modifier.width(4.dp))
                        }
                        Text(
                            text = match.teamB ?: "Unknown", 
                            fontWeight = if (isTeamBWinner) FontWeight.ExtraBold else FontWeight.Bold, 
                            fontSize = 15.sp,
                            color = if (isTeamBWinner) Color(0xFF1E40AF) else Color.Unspecified
                        )
                    }
                    Text(text = teamBScore, color = Color(0xFF64748B), fontSize = 13.sp)
                }
            }

            HorizontalDivider(modifier = Modifier.padding(vertical = 12.dp), color = Color(0xFFF1F5F9))
            
            val resultDisplay = if (!match.winner.isNullOrEmpty()) {
                if (match.winner.contains("Draw", ignoreCase = true)) "Match Drawn"
                else "${match.winner} won the match"
            } else {
                match.result ?: "No Result Available"
            }

            Text(
                text = resultDisplay,
                color = Color(0xFF059669),
                fontWeight = FontWeight.Bold,
                fontSize = 13.sp
            )
        }
    }
}

@Composable
fun CompletedMatchDetail(match: CompletedMatchInfo, onBack: () -> Unit) {
    var selectedTab by remember { mutableStateOf("Match Result") }
    var matchWithScores by remember { mutableStateOf(match) }
    var isScoreLoading by remember { mutableStateOf(false) }
    var apiPredictions by remember { mutableStateOf<MatchPredictions?>(null) }
    var isPredictionsLoading by remember { mutableStateOf(false) }

    LaunchedEffect(match.matchId) {
        isScoreLoading = true
        try {
            val scoreA = RetrofitClient.apiService.getScoreboard(match.matchId.toString(), 1)
            val scoreB = RetrofitClient.apiService.getScoreboard(match.matchId.toString(), 2)
            
            if (scoreA.isSuccessful || scoreB.isSuccessful) {
                matchWithScores = matchWithScores.copy(
                    teamARuns = scoreA.body()?.runs ?: match.teamARuns,
                    teamAWickets = scoreA.body()?.wickets ?: match.teamAWickets,
                    teamAOvers = scoreA.body()?.overs ?: match.teamAOvers,
                    teamBRuns = scoreB.body()?.runs ?: match.teamBRuns,
                    teamBWickets = scoreB.body()?.wickets ?: match.teamBWickets,
                    teamBOvers = scoreB.body()?.overs ?: match.teamBOvers
                )
            }
        } catch (e: Exception) {
            e.printStackTrace()
        } finally {
            isScoreLoading = false
        }
    }

    LaunchedEffect(selectedTab, match.matchId) {
        if (selectedTab == "Predictions" && apiPredictions == null) {
            isPredictionsLoading = true
            try {
                val response = RetrofitClient.apiService.getMatchPredictions(match.matchId.toString())
                if (response.isSuccessful) {
                    apiPredictions = response.body()
                }
            } catch (e: Exception) {
                e.printStackTrace()
            } finally {
                isPredictionsLoading = false
            }
        }
    }

    val oversA = String.format(Locale.US, "%.1f", matchWithScores.teamAOvers)
    val oversB = String.format(Locale.US, "%.1f", matchWithScores.teamBOvers)

    val teamAScore = "${matchWithScores.teamARuns}/${matchWithScores.teamAWickets} ($oversA)"
    val teamBScore = "${matchWithScores.teamBRuns}/${matchWithScores.teamBWickets} ($oversB)"

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFFF8FAFC))
    ) {
        // detail Header
        Surface(
            modifier = Modifier.fillMaxWidth(),
            color = Color(0xFF1E40AF)
        ) {
            Column(
                modifier = Modifier
                    .padding(top = 48.dp, bottom = 20.dp, start = 16.dp, end = 16.dp)
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, "Back", tint = Color.White)
                    }
                    Spacer(Modifier.width(16.dp))
                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            text = "${match.teamA ?: "Team A"} vs ${match.teamB ?: "Team B"}",
                            color = Color.White,
                            fontSize = 16.sp,
                            fontWeight = FontWeight.Bold
                        )
                        Text(
                            text = "${match.venue ?: "Venue"} • T20",
                            color = Color.White.copy(alpha = 0.7f),
                            fontSize = 12.sp
                        )
                    }
                    Surface(
                        color = Color.White.copy(alpha = 0.2f),
                        shape = RoundedCornerShape(16.dp)
                    ) {
                        Text(
                            text = "COMPLETED",
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                            color = Color.White,
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Bold
                        )
                    }
                }

                Spacer(Modifier.height(24.dp))

                // Tab Switcher
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .background(Color.White.copy(alpha = 0.1f), RoundedCornerShape(12.dp))
                        .padding(4.dp)
                ) {
                    MatchTabButton(
                        text = "Match Result",
                        icon = null,
                        isSelected = selectedTab == "Match Result",
                        modifier = Modifier.weight(1f),
                        onClick = { selectedTab = "Match Result" }
                    )
                    MatchTabButton(
                        text = "Predictions",
                        icon = null,
                        isSelected = selectedTab == "Predictions",
                        modifier = Modifier.weight(1f),
                        onClick = { selectedTab = "Predictions" }
                    )
                }
            }
        }

        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            if (selectedTab == "Match Result") {
                // Winner Banner
                Surface(
                    modifier = Modifier.fillMaxWidth(),
                    color = Color(0xFFFFFBEB),
                    shape = RoundedCornerShape(24.dp),
                    border = BorderStroke(1.dp, Color(0xFFFDE68A))
                ) {
                    Column(
                        modifier = Modifier.padding(24.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Surface(
                            modifier = Modifier.size(56.dp),
                            color = Color(0xFFFEF3C7),
                            shape = CircleShape
                        ) {
                            Box(contentAlignment = Alignment.Center) {
                                Icon(Icons.Default.EmojiEvents, null, tint = Color(0xFFD97706), modifier = Modifier.size(32.dp))
                            }
                        }
                        Spacer(Modifier.height(16.dp))
                        Text(text = "Match Result", color = Color(0xFF92400E), fontSize = 14.sp)
                        
                        val resultText = if (!match.winner.isNullOrEmpty()) {
                            if (match.winner.contains("Draw", ignoreCase = true)) "Match Drawn"
                            else "${match.winner} won the match"
                        } else {
                            match.result ?: "No Result Available"
                        }
                        
                        Text(
                            text = resultText,
                            color = Color(0xFF92400E),
                            fontSize = 20.sp,
                            fontWeight = FontWeight.ExtraBold,
                            textAlign = TextAlign.Center
                        )
                    }
                }

                // Full Scorecard
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(20.dp),
                    colors = CardDefaults.cardColors(containerColor = Color.White),
                    border = CardDefaults.outlinedCardBorder()
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Box(modifier = Modifier.width(4.dp).height(16.dp).background(Color(0xFF1E40AF), RoundedCornerShape(2.dp)))
                            Spacer(Modifier.width(8.dp))
                            Text(text = "Full Scorecard", fontWeight = FontWeight.Bold, fontSize = 16.sp)
                            if (isScoreLoading) {
                                Spacer(Modifier.width(8.dp))
                                CircularProgressIndicator(modifier = Modifier.size(16.dp), strokeWidth = 2.dp, color = Color(0xFF1E40AF))
                            }
                        }
                        Spacer(Modifier.height(20.dp))
                        
                        InningsRow(
                            title = "1st Innings",
                            teamName = matchWithScores.teamA ?: "Team A",
                            score = teamAScore,
                            runs = matchWithScores.teamARuns.toString(),
                            wickets = matchWithScores.teamAWickets.toString(),
                            overNum = oversA,
                            color = Color(0xFF1E40AF)
                        )
                        HorizontalDivider(modifier = Modifier.padding(vertical = 20.dp), color = Color(0xFFF1F5F9))
                        InningsRow(
                            title = "2nd Innings",
                            teamName = matchWithScores.teamB ?: "Team B",
                            score = teamBScore,
                            runs = matchWithScores.teamBRuns.toString(),
                            wickets = matchWithScores.teamBWickets.toString(),
                            overNum = oversB,
                            color = Color(0xFF3B82F6)
                        )
                    }
                }
            } else {
                if (isPredictionsLoading) {
                    Box(modifier = Modifier.fillMaxWidth().height(200.dp), contentAlignment = Alignment.Center) {
                        CircularProgressIndicator(color = Color(0xFF1E40AF))
                    }
                } else {
                    val liveData = LiveMatchData(
                        matchId = matchWithScores.matchId,
                        teamA = matchWithScores.teamA,
                        teamB = matchWithScores.teamB,
                        venue = matchWithScores.venue,
                        runs = matchWithScores.teamBRuns,
                        wickets = matchWithScores.teamBWickets,
                        overs = matchWithScores.teamBOvers,
                        crr = if (matchWithScores.teamBOvers > 0) (matchWithScores.teamBRuns / matchWithScores.teamBOvers) else 0f
                    )
                    PredictionsContentIntegrated(match = liveData, apiPredictions = apiPredictions)
                }
            }
        }
    }
}

@Composable
fun MatchTabButton(
    text: String,
    icon: ImageVector?,
    isSelected: Boolean,
    modifier: Modifier = Modifier,
    onClick: () -> Unit
) {
    Surface(
        modifier = modifier
            .padding(2.dp)
            .clickable(onClick = onClick),
        color = if (isSelected) Color.White else Color.Transparent,
        shape = RoundedCornerShape(8.dp),
        shadowElevation = if (isSelected) 2.dp else 0.dp
    ) {
        Row(
            modifier = Modifier.padding(vertical = 8.dp),
            horizontalArrangement = Arrangement.Center,
            verticalAlignment = Alignment.CenterVertically
        ) {
            if (icon != null) {
                Icon(
                    icon,
                    null,
                    tint = if (isSelected) Color(0xFF1E40AF) else Color.White.copy(alpha = 0.7f),
                    modifier = Modifier.size(16.dp)
                )
                Spacer(Modifier.width(8.dp))
            }
            Text(
                text = text,
                color = if (isSelected) Color(0xFF1E40AF) else Color.White.copy(alpha = 0.7f),
                fontSize = 12.sp,
                fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal
            )
        }
    }
}

@Composable
fun InningsRow(
    title: String,
    teamName: String,
    score: String,
    runs: String,
    wickets: String,
    overNum: String,
    color: Color
) {
    Column {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.Bottom
        ) {
            Column {
                Text(text = title, color = Color(0xFF64748B), fontSize = 12.sp)
                Text(text = teamName, fontWeight = FontWeight.ExtraBold, fontSize = 18.sp, color = color)
            }
            Text(text = score, fontWeight = FontWeight.Bold, fontSize = 20.sp)
        }
        
        Spacer(Modifier.height(12.dp))
        
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .background(Color(0xFFF8FAFC), RoundedCornerShape(8.dp))
                .padding(12.dp),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            ScoreDetailItem("Runs", runs)
            ScoreDetailItem("Wickets", wickets)
            ScoreDetailItem("Overs", overNum)
        }
    }
}

@Composable
fun ScoreDetailItem(label: String, value: String) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(text = label, color = Color(0xFF94A3B8), fontSize = 10.sp)
        Text(text = value, fontWeight = FontWeight.Bold, fontSize = 14.sp)
    }
}
