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
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.CompareArrows
import androidx.compose.material.icons.automirrored.filled.Undo
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.Sync
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.launch
import java.util.Locale

@Composable
fun ScoringScreen(
    matchId: String,
    teamAName: String,
    teamBName: String,
    teamAPlayers: List<String>,
    teamBPlayers: List<String>,
    initialStriker: String = "",
    initialNonStriker: String = "",
    initialBowler: String = "",
    onBack: () -> Unit,
    onMatchComplete: (CompletedMatchInfo) -> Unit = {}
) {
    val coroutineScope = rememberCoroutineScope()
    val apiService = RetrofitClient.apiService
    val snackbarHostState = remember { SnackbarHostState() }

    var selectedTab by remember { mutableStateOf("Score Update") }
    var currentInnings by remember { mutableIntStateOf(1) }
    
    // UI Dialog States
    var showWhoOutDialog by remember { mutableStateOf(false) }
    var showSelectNextBatsmanDialog by remember { mutableStateOf(false) }
    var showSelectStrikerDialog by remember { mutableStateOf(false) }
    var showSelectNonStrikerDialog by remember { mutableStateOf(false) }
    var showChangeBowlerDialog by remember { mutableStateOf(false) }
    var showOverCompleteDialog by remember { mutableStateOf(false) }
    var showEndInningsDialog by remember { mutableStateOf(false) }
    var showEndMatchDialog by remember { mutableStateOf(false) }

    var outPosition by remember { mutableStateOf("") }
    
    val currentBattingTeam = if (currentInnings == 1) teamAName else teamBName
    val battingPlayers = if (currentInnings == 1) teamAPlayers else teamBPlayers
    val bowlingPlayers = if (currentInnings == 1) teamBPlayers else teamAPlayers

    // Scoreboard State
    var totalRuns by remember { mutableIntStateOf(0) }
    var totalWickets by remember { mutableIntStateOf(0) }
    var totalOvers by remember { mutableFloatStateOf(0.0f) }
    var currentCRR by remember { mutableFloatStateOf(0.0f) }
    var firstInningsScore by remember { mutableStateOf<ScoreResponse?>(null) }
    
    // Manual Edit State
    var isManualScore by remember { mutableStateOf(false) }
    var editableRuns by remember(totalRuns) { mutableStateOf(totalRuns.toString()) }
    var editableWickets by remember(totalWickets) { mutableStateOf(totalWickets.toString()) }
    var editableOvers by remember(totalOvers) { mutableStateOf(String.format(Locale.US, "%.1f", totalOvers)) }

    // Stats
    var batsmenStats by remember { mutableStateOf(emptyList<BatsmanStat>()) }
    var bowlersStats by remember { mutableStateOf(emptyList<BowlerStat>()) }
    var partnershipData by remember { mutableStateOf(PartnershipResponse(0, 0)) }
    var lastSixBalls by remember { mutableStateOf(emptyList<String>()) }

    // Current Players State
    var striker by remember { mutableStateOf(initialStriker) }
    var nonStriker by remember { mutableStateOf(initialNonStriker) }
    var currentBowlerName by remember { mutableStateOf(initialBowler) }

    val dismissedPlayers = remember { mutableStateListOf<String>() }
    
    // Predictions State
    var apiPredictions by remember { mutableStateOf<MatchPredictions?>(null) }

    // Extras support state
    var selectedExtraType by remember { mutableStateOf("NONE") }

    fun refreshMatchData(isBallInput: Boolean = false) {
        if (!isManualScore) {
            coroutineScope.launch {
                try {
                    val scoreRes = apiService.getScoreboard(matchId, currentInnings)
                    if (scoreRes.isSuccessful) {
                        scoreRes.body()?.let {
                            val prevOvers = totalOvers
                            totalRuns = it.runs
                            totalWickets = it.wickets
                            totalOvers = it.overs
                            currentCRR = it.crr
                            if (!it.striker.isNullOrEmpty()) striker = it.striker!!
                            if (!it.nonStriker.isNullOrEmpty()) nonStriker = it.nonStriker!!
                            if (!it.bowler.isNullOrEmpty()) currentBowlerName = it.bowler!!
                            
                            if (isBallInput && it.overs.toInt() > prevOvers.toInt() && it.overs > 0) {
                                showOverCompleteDialog = true
                            }
                        }
                    }

                    if (currentInnings == 2 && firstInningsScore == null) {
                        val firstRes = apiService.getScoreboard(matchId, 1)
                        if (firstRes.isSuccessful) {
                            firstInningsScore = firstRes.body()
                        }
                    }

                    val batsmenRes = apiService.getBatsmenStats(matchId)
                    if (batsmenRes.isSuccessful) {
                        batsmenStats = batsmenRes.body() ?: emptyList()
                    }

                    val bowlerRes = apiService.getBowlerStats(matchId)
                    if (bowlerRes.isSuccessful) {
                        bowlersStats = bowlerRes.body() ?: emptyList()
                    }

                    val partRes = apiService.getPartnership(matchId, currentInnings)
                    if (partRes.isSuccessful) {
                        partnershipData = partRes.body() ?: PartnershipResponse(0, 0)
                    }

                    val last6Res = apiService.getLast6Balls(matchId, currentInnings)
                    if (last6Res.isSuccessful) {
                        lastSixBalls = last6Res.body() ?: emptyList()
                    }
                    
                    if (selectedTab == "Predictions") {
                        val predRes = apiService.getMatchPredictions(matchId)
                        if (predRes.isSuccessful) {
                            apiPredictions = predRes.body()
                        }
                    }
                } catch (e: Exception) {
                    // Network error handling
                }
            }
        }
    }

    LaunchedEffect(matchId, selectedTab, currentInnings) {
        refreshMatchData()
    }

    fun updateFromEditable() {
        isManualScore = true
        val r = editableRuns.toIntOrNull() ?: totalRuns
        val w = editableWickets.toIntOrNull() ?: totalWickets
        val o = editableOvers.toFloatOrNull() ?: totalOvers
        
        totalRuns = r
        totalWickets = w
        totalOvers = o
        
        val totalBalls = (o.toInt() * 6) + ((o * 10).toInt() % 10)
        currentCRR = if (totalBalls > 0) (r.toFloat() / (totalBalls / 6.0f)) else 0.0f
    }

    fun undoLastBall() {
        coroutineScope.launch {
            try {
                val res = apiService.undoBall(matchId)
                if (res.isSuccessful) {
                    isManualScore = false
                    refreshMatchData()
                    snackbarHostState.showSnackbar("Last ball undone")
                } else {
                    snackbarHostState.showSnackbar("Undo failed")
                }
            } catch (e: Exception) {
                snackbarHostState.showSnackbar("Network error")
            }
        }
    }

    fun submitBall(
        runs: Int,
        extrasType: String = "NONE",
        extrasRuns: Int = 0,
        wicket: Int = 0,
        wicketType: String? = null
    ) {
        if (striker.isEmpty() || currentBowlerName.isEmpty()) {
            coroutineScope.launch {
                snackbarHostState.showSnackbar("Select Striker and Bowler first!")
            }
            return
        }

        coroutineScope.launch {
            try {
                val request = BallInputRequest(
                    matchId = matchId.toInt(),
                    innings = currentInnings,
                    batsman = striker,
                    bowler = currentBowlerName,
                    runs = runs,
                    extrasType = extrasType,
                    extras = extrasRuns,
                    wicket = wicket,
                    wicketType = wicketType
                )

                val res = apiService.submitBall(request)

                if (res.isSuccessful) {
                    refreshMatchData(isBallInput = true)
                } else {
                    snackbarHostState.showSnackbar("Error: ${res.message()}")
                }
            } catch (e: Exception) {
                snackbarHostState.showSnackbar("Check connection!")
            }
        }
    }

    fun finalizeWicket(player: String) {
        dismissedPlayers.add(player)
        outPosition = if (player == striker) "striker" else "non-striker"
        showWhoOutDialog = false
        showSelectNextBatsmanDialog = true

        val wType = when (selectedExtraType) {
            "NOBALL" -> "RUNOUT"
            "WIDE" -> "STUMPED"
            else -> "OUT"
        }
        
        val exType = selectedExtraType
        val exRuns = if (exType == "WIDE" || exType == "NOBALL") 1 else 0

        submitBall(
            runs = 0,
            extrasType = exType,
            extrasRuns = exRuns,
            wicket = 1,
            wicketType = wType
        )
        selectedExtraType = "NONE"
    }

    fun handleMatchCompletion(winnerName: String) {
        coroutineScope.launch {
            try {
                val resultText = when {
                    winnerName == teamAName -> "$teamAName won"
                    winnerName == teamBName -> "$teamBName won"
                    else -> "Match Drawn"
                }
                val res = apiService.endMatch(EndMatchRequest(matchId, winnerName, resultText))
                if (res.isSuccessful) {
                    val completedInfo = CompletedMatchInfo(
                        matchId = matchId.toIntOrNull() ?: 0,
                        teamA = teamAName,
                        teamB = teamBName,
                        venue = "Local Ground",
                        teamARuns = firstInningsScore?.runs ?: totalRuns,
                        teamAWickets = firstInningsScore?.wickets ?: totalWickets,
                        teamAOvers = firstInningsScore?.overs ?: totalOvers,
                        teamBRuns = if (currentInnings == 2) totalRuns else 0,
                        teamBWickets = if (currentInnings == 2) totalWickets else 0,
                        teamBOvers = if (currentInnings == 2) totalOvers else 0.0f,
                        winner = winnerName,
                        result = resultText
                    )
                    onMatchComplete(completedInfo)
                }
            } catch (e: Exception) {
                snackbarHostState.showSnackbar("Failed to end match")
            }
        }
    }

    Scaffold(
        snackbarHost = { SnackbarHost(snackbarHostState) },
        bottomBar = {
            if (selectedTab == "Score Update") {
                Surface(
                    modifier = Modifier.fillMaxWidth(),
                    shadowElevation = 8.dp,
                    color = Color.White
                ) {
                    Row(
                        modifier = Modifier
                            .padding(horizontal = 16.dp, vertical = 12.dp)
                            .navigationBarsPadding(),
                        horizontalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        OutlinedButton(
                            onClick = { undoLastBall() },
                            modifier = Modifier.weight(1f).height(48.dp),
                            shape = RoundedCornerShape(12.dp),
                            border = BorderStroke(1.dp, Color(0xFF64748B))
                        ) {
                            Icon(Icons.AutoMirrored.Filled.Undo, null, modifier = Modifier.size(18.dp))
                            Spacer(Modifier.width(6.dp))
                            Text("Undo Ball", fontSize = 14.sp, fontWeight = FontWeight.Bold)
                        }

                        Button(
                            onClick = {
                                if (currentInnings == 1) showEndInningsDialog = true else showEndMatchDialog = true
                            },
                            modifier = Modifier.weight(1f).height(48.dp),
                            colors = ButtonDefaults.buttonColors(
                                containerColor = if (currentInnings == 1) Color(0xFF3B82F6) else Color(0xFFEF4444)
                            ),
                            shape = RoundedCornerShape(12.dp)
                        ) {
                            Icon(if (currentInnings == 1) Icons.Default.SkipNext else Icons.Default.Stop, null, modifier = Modifier.size(18.dp))
                            Spacer(Modifier.width(6.dp))
                            Text(if (currentInnings == 1) "End Innings" else "End Match", fontSize = 14.sp, fontWeight = FontWeight.Bold)
                        }
                    }
                }
            }
        }
    ) { padding ->
        Column(modifier = Modifier.fillMaxSize().background(Color(0xFFF8FAFC)).padding(padding)) {
            // Header
            Box(
                modifier = Modifier.fillMaxWidth().background(brush = Brush.verticalGradient(colors = listOf(Color(0xFF1E40AF), Color(0xFF3B82F6)))).padding(top = 40.dp, bottom = 20.dp)
            ) {
                Column {
                    Row(modifier = Modifier.fillMaxWidth().padding(horizontal = 8.dp), verticalAlignment = Alignment.CenterVertically) {
                        IconButton(onClick = onBack) { Icon(Icons.AutoMirrored.Filled.ArrowBack, "Back", tint = Color.White) }
                        Column(modifier = Modifier.weight(1f)) {
                            Text("$teamAName vs $teamBName", color = Color.White, fontSize = 16.sp, fontWeight = FontWeight.Bold)
                            Text("Innings $currentInnings", color = Color.White.copy(alpha = 0.7f), fontSize = 12.sp)
                        }
                        IconButton(onClick = { 
                            isManualScore = false
                            refreshMatchData() 
                        }) { Icon(Icons.Default.Refresh, "Refresh", tint = Color.White) }
                    }
                    
                    Row(modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp).fillMaxWidth().height(40.dp).background(Color.White.copy(alpha = 0.15f), RoundedCornerShape(20.dp)).padding(4.dp)) {
                        listOf("Score Update", "Predictions").forEach { tab ->
                            val isSelected = selectedTab == tab
                            Box(modifier = Modifier.weight(1f).fillMaxHeight().background(if (isSelected) Color.White else Color.Transparent, RoundedCornerShape(18.dp)).clickable { selectedTab = tab }, contentAlignment = Alignment.Center) {
                                Text(tab, color = if (isSelected) Color(0xFF1E40AF) else Color.White, fontSize = 13.sp, fontWeight = FontWeight.Bold)
                            }
                        }
                    }
                }
            }

            Column(modifier = Modifier.weight(1f).verticalScroll(rememberScrollState()).padding(16.dp), verticalArrangement = Arrangement.spacedBy(16.dp)) {
                // Shared Score Card - Now Editable
                Surface(
                    modifier = Modifier.fillMaxWidth(),
                    color = Color(0xFFEFF6FF),
                    shape = RoundedCornerShape(24.dp),
                    border = BorderStroke(1.dp, Color(0xFFDBEAFE))
                ) {
                    Column(modifier = Modifier.padding(24.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                        Text(currentBattingTeam, color = Color(0xFF64748B), fontSize = 14.sp, fontWeight = FontWeight.Bold)
                        
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            BasicTextField(
                                value = editableRuns,
                                onValueChange = { 
                                    editableRuns = it
                                    updateFromEditable()
                                },
                                textStyle = TextStyle(fontSize = 52.sp, fontWeight = FontWeight.ExtraBold, color = Color(0xFF1E40AF), textAlign = TextAlign.Center),
                                modifier = Modifier.width(IntrinsicSize.Min).defaultMinSize(minWidth = 40.dp),
                                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
                            )
                            Text("/", fontSize = 52.sp, fontWeight = FontWeight.ExtraBold, color = Color(0xFF1E40AF))
                            BasicTextField(
                                value = editableWickets,
                                onValueChange = { 
                                    editableWickets = it
                                    updateFromEditable()
                                },
                                textStyle = TextStyle(fontSize = 52.sp, fontWeight = FontWeight.ExtraBold, color = Color(0xFF1E40AF), textAlign = TextAlign.Center),
                                modifier = Modifier.width(IntrinsicSize.Min).defaultMinSize(minWidth = 20.dp),
                                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
                            )
                        }

                        Row(verticalAlignment = Alignment.CenterVertically) {
                            BasicTextField(
                                value = editableOvers,
                                onValueChange = { 
                                    editableOvers = it
                                    updateFromEditable()
                                },
                                textStyle = TextStyle(color = Color(0xFF64748B), fontSize = 16.sp, textAlign = TextAlign.End),
                                modifier = Modifier.width(IntrinsicSize.Min).defaultMinSize(minWidth = 30.dp),
                                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal)
                            )
                            Text(" Overs", color = Color(0xFF64748B), fontSize = 16.sp)
                            Spacer(Modifier.width(16.dp))
                            Text("CRR: ${String.format(Locale.US, "%.2f", currentCRR)}", color = Color(0xFF1E40AF), fontSize = 16.sp, fontWeight = FontWeight.Bold)
                        }
                        
                        if (currentInnings == 2 && firstInningsScore != null) {
                            Spacer(Modifier.height(8.dp))
                            val target = firstInningsScore!!.runs + 1
                            val needed = target - totalRuns
                            Text("Target: $target (Need $needed runs)", color = Color(0xFF1E40AF), fontSize = 14.sp, fontWeight = FontWeight.Bold)
                        }
                        
                        if (isManualScore) {
                            Text("Simulation Mode (Manual Edits)", color = Color(0xFFF97316), fontSize = 11.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(top = 4.dp))
                        }
                    }
                }

                if (selectedTab == "Score Update") {
                    // Partnership & Last Balls
                    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                        Card(modifier = Modifier.weight(0.7f), shape = RoundedCornerShape(16.dp), colors = CardDefaults.cardColors(containerColor = Color.White)) {
                            Column(modifier = Modifier.padding(12.dp)) {
                                Text("Partnership", fontSize = 11.sp, color = Color.Gray)
                                Text("${partnershipData.runs} (${partnershipData.balls})", fontWeight = FontWeight.Bold, fontSize = 16.sp)
                            }
                        }
                        Card(modifier = Modifier.weight(1.3f), shape = RoundedCornerShape(16.dp), colors = CardDefaults.cardColors(containerColor = Color.White)) {
                            Column(modifier = Modifier.padding(12.dp)) {
                                Text("Last 6 Balls", fontSize = 11.sp, color = Color.Gray)
                                Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                                    lastSixBalls.takeLast(6).forEach { ball ->
                                        val displayText = ball

                                        Surface(
                                            modifier = Modifier
                                                .padding(horizontal = 2.dp)
                                                .size(22.dp),
                                            shape = CircleShape,
                                            color = when {
                                                displayText.startsWith("W") && displayText != "Wd" -> Color(0xFFEF4444)
                                                displayText.contains("4") || displayText.contains("6") -> Color(0xFF10B981)
                                                displayText.contains("Wd") || displayText.contains("Nb") -> Color(0xFFF97316)
                                                else -> Color(0xFFF1F5F9)
                                            }
                                        ) {
                                            Box(contentAlignment = Alignment.Center) {
                                                Text(
                                                    text = displayText,
                                                    fontSize = 10.sp,
                                                    fontWeight = FontWeight.Bold,
                                                    color = if(displayText.contains("W") || displayText.contains("Nb") || displayText.contains("4") || displayText.contains("6"))
                                                        Color.White
                                                    else
                                                        Color(0xFF64748B)
                                                )
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }

                    // Batsmen Section
                    ScoringSectionCard(title = "Batsmen", actionIcon = Icons.AutoMirrored.Filled.CompareArrows, onActionClick = { 
                        val t = striker; striker = nonStriker; nonStriker = t 
                    }) {
                        if (striker.isEmpty() && nonStriker.isEmpty()) {
                            Text("Tap to select batsmen", color = Color.Gray, fontSize = 14.sp, modifier = Modifier.fillMaxWidth().clickable { showSelectStrikerDialog = true }.padding(12.dp))
                        } else {
                            val sStat = batsmenStats.find { it.batsman == striker } ?: BatsmanStat(striker, 0, 0, 0, 0, 0.0)
                            val nsStat = batsmenStats.find { it.batsman == nonStriker } ?: BatsmanStat(nonStriker, 0, 0, 0, 0, 0.0)
                            
                            BatsmanRowItem(sStat.batsman ?: "Striker", sStat.runs, sStat.balls, sStat.fours, sStat.sixes, true, onClick = { showSelectStrikerDialog = true })
                            BatsmanRowItem(nsStat.batsman ?: "Non-Striker", nsStat.runs, nsStat.balls, nsStat.fours, nsStat.sixes, false, onClick = { showSelectNonStrikerDialog = true })
                        }
                    }

                    // Bowler Section
                    ScoringSectionCard(title = "Bowler", actionIcon = Icons.Outlined.Sync, onActionClick = { showChangeBowlerDialog = true }) {
                        val bowler = bowlersStats.find { it.bowler == currentBowlerName }
                        if (currentBowlerName.isEmpty()) {
                            Text("Tap to select bowler", color = Color.Gray, fontSize = 14.sp, modifier = Modifier.fillMaxWidth().clickable { showChangeBowlerDialog = true }.padding(12.dp))
                        } else {
                            BowlerRowItem(currentBowlerName, bowler?.overs ?: "0.0", bowler?.runs ?: 0, bowler?.wickets ?: 0, String.format(Locale.US, "%.2f", bowler?.economy ?: 0.0), onClick = { showChangeBowlerDialog = true })
                        }
                    }

                    // Run Buttons
                    Card(modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(16.dp), colors = CardDefaults.cardColors(containerColor = Color.White)) {
                        Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                                listOf("0", "1", "2", "3", "4", "6").forEach { runValue ->
                                    val r = runValue.toInt()
                                    RunCircleButton(runValue) {
                                        when (selectedExtraType) {
                                            "WIDE" -> submitBall(runs = 0, extrasType = "WIDE", extrasRuns = r + 1)
                                            "NOBALL" -> submitBall(runs = r, extrasType = "NOBALL", extrasRuns = 1)
                                            "PENALTY" -> submitBall(runs = 0, extrasType = "PENALTY", extrasRuns = r)
                                            else -> submitBall(runs = r)
                                        }
                                        selectedExtraType = "NONE"
                                    }
                                }
                            }
                            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                ActionPillButton(
                                    text = if (selectedExtraType == "WIDE") "WIDE [X]" else "Wide",
                                    color = if (selectedExtraType == "WIDE") Color.DarkGray else Color(0xFFF97316),
                                    modifier = Modifier.weight(1f)
                                ) {
                                    selectedExtraType = if (selectedExtraType == "WIDE") "NONE" else "WIDE"
                                }
                                ActionPillButton(
                                    text = if (selectedExtraType == "NOBALL") "NO BALL [X]" else "No Ball",
                                    color = if (selectedExtraType == "NOBALL") Color.DarkGray else Color(0xFFF97316),
                                    modifier = Modifier.weight(1f)
                                ) {
                                    selectedExtraType = if (selectedExtraType == "NOBALL") "NONE" else "NOBALL"
                                }
                                ActionPillButton(
                                    text = if (selectedExtraType == "PENALTY") "PNLTY [X]" else "Penalty",
                                    color = if (selectedExtraType == "PENALTY") Color.DarkGray else Color(0xFF64748B),
                                    modifier = Modifier.weight(1f)
                                ) {
                                    selectedExtraType = if (selectedExtraType == "PENALTY") "NONE" else "PENALTY"
                                }
                                ActionPillButton("Wicket", Color(0xFFEF4444), Modifier.weight(1f)) {
                                    showWhoOutDialog = true
                                }
                            }
                        }
                    }
                } else {
                    // Predictions Tab
                    val currentMatchData = LiveMatchData(
                        matchId = matchId.toIntOrNull() ?: 0,
                        teamA = teamAName,
                        teamB = teamBName,
                        venue = "Live Match",
                        runs = totalRuns,
                        wickets = totalWickets,
                        overs = totalOvers,
                        crr = currentCRR,
                        striker = striker,
                        nonStriker = nonStriker,
                        strikerRuns = batsmenStats.find { it.batsman == striker }?.runs ?: 0,
                        nonStrikerRuns = batsmenStats.find { it.batsman == nonStriker }?.runs ?: 0
                    )
                    
                    PredictionsContentIntegrated(
                        match = currentMatchData,
                        apiPredictions = if (isManualScore) null else apiPredictions
                    )
                }
            }
        }
    }

    // Dialogs
    if (showSelectStrikerDialog) {
        SelectPlayerDialog("Select Striker", battingPlayers.filter { it != nonStriker }, { showSelectStrikerDialog = false }) { striker = it; showSelectStrikerDialog = false }
    }
    if (showSelectNonStrikerDialog) {
        SelectPlayerDialog("Select Non-Striker", battingPlayers.filter { it != striker }, { showSelectNonStrikerDialog = false }) { nonStriker = it; showSelectNonStrikerDialog = false }
    }
    if (showChangeBowlerDialog || showOverCompleteDialog) {
        SelectPlayerDialog("Select Bowler", bowlingPlayers, { showChangeBowlerDialog = false; showOverCompleteDialog = false }) { currentBowlerName = it; showChangeBowlerDialog = false; showOverCompleteDialog = false }
    }
    if (showWhoOutDialog) {
        WhoGotOutDialog(striker, nonStriker, { showWhoOutDialog = false }, { finalizeWicket(it) })
    }
    if (showSelectNextBatsmanDialog) {
        val available = battingPlayers.filter { it !in dismissedPlayers && it != striker && it != nonStriker }
        SelectPlayerDialog("Select Next Batsman", available, { showSelectNextBatsmanDialog = false }) { if (outPosition == "striker") striker = it else nonStriker = it; showSelectNextBatsmanDialog = false }
    }
    
    if (showEndInningsDialog) {
        AlertDialog(
            onDismissRequest = { showEndInningsDialog = false },
            title = { Text("End Innings") },
            text = { Text("Are you sure you want to end this innings and start the next one?") },
            confirmButton = {
                TextButton(onClick = {
                    currentInnings = 2
                    striker = ""; nonStriker = ""; currentBowlerName = ""
                    dismissedPlayers.clear()
                    isManualScore = false
                    refreshMatchData()
                    showEndInningsDialog = false
                    coroutineScope.launch { snackbarHostState.showSnackbar("Switched to 2nd Innings") }
                }) { Text("Confirm") }
            },
            dismissButton = {
                TextButton(onClick = { showEndInningsDialog = false }) { Text("Cancel") }
            }
        )
    }

    if (showEndMatchDialog) {
        AlertDialog(
            onDismissRequest = { showEndMatchDialog = false },
            title = { Text("End Match") },
            text = { Text("Select the winner of this match:") },
            confirmButton = {
                Column(modifier = Modifier.fillMaxWidth().padding(8.dp)) {
                    Button(
                        onClick = { 
                            handleMatchCompletion(teamAName)
                            showEndMatchDialog = false 
                        },
                        modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF1E40AF))
                    ) { Text(teamAName) }
                    
                    Button(
                        onClick = { 
                            handleMatchCompletion(teamBName)
                            showEndMatchDialog = false 
                        },
                        modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF3B82F6))
                    ) { Text(teamBName) }
                    
                    TextButton(
                        onClick = { 
                            handleMatchCompletion("Draw")
                            showEndMatchDialog = false 
                        },
                        modifier = Modifier.align(Alignment.CenterHorizontally)
                    ) { Text("It's a Draw") }
                }
            },
            dismissButton = {
                TextButton(onClick = { showEndMatchDialog = false }) { Text("Cancel") }
            }
        )
    }
}

@Composable
fun SelectPlayerDialog(title: String, players: List<String>, onDismiss: () -> Unit, onSelect: (String) -> Unit) {
    AlertDialog(onDismissRequest = onDismiss, title = { Text(title) }, text = {
        LazyColumn(modifier = Modifier.fillMaxWidth()) {
            items(players) { player ->
                Surface(modifier = Modifier.fillMaxWidth().clickable { onSelect(player) }.padding(vertical = 8.dp), shape = RoundedCornerShape(8.dp), color = Color(0xFFF1F5F9)) {
                    Text(player, modifier = Modifier.padding(16.dp), fontWeight = FontWeight.Bold)
                }
            }
        }
    }, confirmButton = {}, dismissButton = { TextButton(onClick = onDismiss) { Text("Cancel") } })
}

@Composable
fun ScoringSectionCard(title: String, actionIcon: ImageVector, onActionClick: () -> Unit, content: @Composable () -> Unit) {
    Card(modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(16.dp), colors = CardDefaults.cardColors(containerColor = Color.White)) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                Text(title, fontWeight = FontWeight.Bold, color = Color(0xFF1E293B))
                IconButton(onClick = onActionClick) { Icon(actionIcon, null, modifier = Modifier.size(20.dp), tint = Color(0xFF3B82F6)) }
            }
            content()
        }
    }
}

@Composable
fun BatsmanRowItem(name: String, runs: Int, balls: Int, fours: Int, sixes: Int, isOnStrike: Boolean, onClick: () -> Unit) {
    Row(modifier = Modifier.fillMaxWidth().clickable { onClick() }.padding(vertical = 8.dp), verticalAlignment = Alignment.CenterVertically) {
        Row(modifier = Modifier.weight(1f), verticalAlignment = Alignment.CenterVertically) {
            if (isOnStrike) Icon(Icons.Default.Bolt, null, tint = Color(0xFFF97316), modifier = Modifier.size(16.dp))
            Text(name.ifBlank { "Select Batsman" }, fontWeight = if (isOnStrike) FontWeight.Bold else FontWeight.Normal, color = if(isOnStrike) Color(0xFF1E40AF) else Color(0xFF1E293B))
        }
        Text("$runs($balls)", fontWeight = FontWeight.Bold, color = Color(0xFF1E293B))
    }
}

@Composable
fun BowlerRowItem(name: String, overs: String, runs: Int, wickets: Int, econ: String, onClick: () -> Unit) {
    Row(modifier = Modifier.fillMaxWidth().clickable { onClick() }.padding(vertical = 8.dp), verticalAlignment = Alignment.CenterVertically) {
        Text(name.ifBlank { "Select Bowler" }, modifier = Modifier.weight(1f), fontWeight = FontWeight.Medium, color = Color(0xFF1E293B))
        Text("$wickets-$runs ($overs)", fontWeight = FontWeight.Bold, color = Color(0xFF1E293B))
    }
}

@Composable
fun RunCircleButton(text: String, onClick: () -> Unit) {
    Surface(onClick = onClick, modifier = Modifier.size(42.dp), color = Color(0xFF1E40AF), shape = CircleShape) {
        Box(contentAlignment = Alignment.Center) { Text(text, color = Color.White, fontWeight = FontWeight.Bold) }
    }
}

@Composable
fun ActionPillButton(text: String, color: Color, modifier: Modifier, onClick: () -> Unit) {
    Button(onClick = onClick, modifier = modifier.height(36.dp), colors = ButtonDefaults.buttonColors(containerColor = color), contentPadding = PaddingValues(horizontal = 8.dp), shape = RoundedCornerShape(8.dp)) {
        Text(text, fontSize = 11.sp, fontWeight = FontWeight.Bold)
    }
}

@Composable
fun WhoGotOutDialog(striker: String, nonStriker: String, onDismiss: () -> Unit, onConfirmOut: (String) -> Unit) {
    AlertDialog(onDismissRequest = onDismiss, title = { Text("Wicket! Who is out?") }, text = {
        Column {
            Button(onClick = { onConfirmOut(striker) }, modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp), colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFEF4444))) { Text(striker) }
            Button(onClick = { onConfirmOut(nonStriker) }, modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp), colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFEF4444))) { Text(nonStriker) }
        }
    }, confirmButton = {}, dismissButton = { TextButton(onClick = onDismiss) { Text("Cancel") } })
}
