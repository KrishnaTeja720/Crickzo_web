package com.simats.crickzo

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.launch

@Composable
fun AddPlayersScreen(
    matchId: Int,
    teamAName: String,
    teamBName: String,
    onBack: () -> Unit,
    onStartMatch: (List<String>, List<String>, String, String, String) -> Unit
) {
    val coroutineScope = rememberCoroutineScope()
    val apiService = RetrofitClient.apiService
    val snackbarHostState = remember { SnackbarHostState() }
    val context = LocalContext.current

    var teamAPlayers by remember { mutableStateOf(listOf<String>()) }
    var teamBPlayers by remember { mutableStateOf(listOf<String>()) }
    
    var playerAInput by remember { mutableStateOf("") }
    var playerBInput by remember { mutableStateOf("") }

    var showStartSetupDialog by remember { mutableStateOf(false) }
    var isStarting by remember { mutableStateOf(false) }

    val playerSuggestions = listOf(
        "Virat Kohli", "Rohit Sharma", "MS Dhoni", "Hardik Pandya", "Jasprit Bumrah", 
        "KL Rahul", "Suryakumar Yadav", "Ravindra Jadeja", "Shubman Gill", "Pat Cummins", 
        "Steve Smith", "David Warner", "Glenn Maxwell", "Mitchell Starc", "Jos Buttler"
    ).distinct().sorted()

    fun handleStartMatchBackend(striker: String, nonStriker: String, bowler: String) {
        if (isStarting) return
        isStarting = true
        coroutineScope.launch {
            try {
                // 1. Setup teams and players using MatchSetupRequest
                val setupReq = MatchSetupRequest(
                    matchId = matchId,
                    teamAPlayers = teamAPlayers,
                    teamBPlayers = teamBPlayers
                )
                val setupRes = apiService.matchSetup(setupReq)
                
                if (setupRes.isSuccessful) {
                    // 2. Start Match with opening pair
                    val startReq = StartMatchRequest(
                        matchId = matchId,
                        striker = striker,
                        nonStriker = nonStriker,
                        bowler = bowler
                    )
                    val startRes = apiService.startMatch(startReq)
                    
                    if (startRes.isSuccessful) {
                        onStartMatch(teamAPlayers, teamBPlayers, striker, nonStriker, bowler)
                    } else {
                        snackbarHostState.showSnackbar("Failed to start match: ${startRes.message()}")
                    }
                } else {
                    snackbarHostState.showSnackbar("Failed to setup players: ${setupRes.message()}")
                }
            } catch (e: Exception) {
                snackbarHostState.showSnackbar("Connection error: ${e.localizedMessage}")
                // Fallback for demo purposes if backend is partially implemented
                onStartMatch(teamAPlayers, teamBPlayers, striker, nonStriker, bowler)
            } finally {
                isStarting = false
                showStartSetupDialog = false
            }
        }
    }

    Scaffold(
        snackbarHost = { SnackbarHost(snackbarHostState) },
        topBar = {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(Color(0xFF1E40AF))
                    .padding(top = 40.dp, bottom = 20.dp, start = 8.dp, end = 16.dp)
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    IconButton(onClick = onBack) {
                        Icon(imageVector = Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back", tint = Color.White)
                    }
                    Column {
                        Text(text = "Add Players", color = Color.White, fontSize = 18.sp, fontWeight = FontWeight.Bold)
                        Text(text = "Step 2 of 2: Team Lineups", color = Color.White.copy(alpha = 0.8f), fontSize = 12.sp)
                    }
                }
            }
        },
        bottomBar = {
            Surface(modifier = Modifier.fillMaxWidth(), color = Color.White, shadowElevation = 8.dp) {
                Button(
                    onClick = { showStartSetupDialog = true },
                    enabled = teamAPlayers.size >= 2 && teamBPlayers.size >= 1 && !isStarting,
                    modifier = Modifier.fillMaxWidth().padding(16.dp).height(56.dp),
                    shape = RoundedCornerShape(12.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF1E40AF))
                ) {
                    if (isStarting) {
                        CircularProgressIndicator(color = Color.White, modifier = Modifier.size(24.dp))
                    } else {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Default.PlayArrow, contentDescription = null)
                            Spacer(Modifier.width(8.dp))
                            Text("Start Match", fontSize = 16.sp, fontWeight = FontWeight.Bold)
                        }
                    }
                }
            }
        }
    ) { innerPadding ->
        LazyColumn(
            modifier = Modifier.fillMaxSize().background(Color(0xFFF8FAFC)).padding(innerPadding).padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
            contentPadding = PaddingValues(vertical = 16.dp)
        ) {
            item {
                TeamCard(
                    teamName = teamAName.ifBlank { "Team A" },
                    players = teamAPlayers,
                    inputValue = playerAInput,
                    onInputChange = { playerAInput = it },
                    onAdd = { if (playerAInput.isNotBlank()) { teamAPlayers = teamAPlayers + playerAInput.trim(); playerAInput = "" } },
                    onRemove = { index -> teamAPlayers = teamAPlayers.toMutableList().apply { removeAt(index) } },
                    suggestions = playerSuggestions
                )
            }
            item {
                TeamCard(
                    teamName = teamBName.ifBlank { "Team B" },
                    players = teamBPlayers,
                    inputValue = playerBInput,
                    onInputChange = { playerBInput = it },
                    onAdd = { if (playerBInput.isNotBlank()) { teamBPlayers = teamBPlayers + playerBInput.trim(); playerBInput = "" } },
                    onRemove = { index -> teamBPlayers = teamBPlayers.toMutableList().apply { removeAt(index) } },
                    suggestions = playerSuggestions
                )
            }
        }
    }

    if (showStartSetupDialog) {
        StartMatchSetupDialog(
            teamAPlayers = teamAPlayers,
            teamBPlayers = teamBPlayers,
            onDismiss = { showStartSetupDialog = false },
            onConfirm = { striker, nonStriker, bowler ->
                handleStartMatchBackend(striker, nonStriker, bowler)
            }
        )
    }
}

@Composable
fun StartMatchSetupDialog(
    teamAPlayers: List<String>,
    teamBPlayers: List<String>,
    onDismiss: () -> Unit,
    onConfirm: (String, String, String) -> Unit
) {
    var striker by remember { mutableStateOf(teamAPlayers.getOrNull(0) ?: "") }
    var nonStriker by remember { mutableStateOf(teamAPlayers.getOrNull(1) ?: "") }
    var bowler by remember { mutableStateOf(teamBPlayers.getOrNull(0) ?: "") }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Match Setup") },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Text("Select Openers", fontWeight = FontWeight.Bold)
                DropdownSelector(label = "Striker", selected = striker, options = teamAPlayers) { striker = it }
                DropdownSelector(label = "Non-Striker", selected = nonStriker, options = teamAPlayers.filter { it != striker }) { nonStriker = it }
                Spacer(Modifier.height(8.dp))
                Text("Select Opening Bowler", fontWeight = FontWeight.Bold)
                DropdownSelector(label = "Bowler", selected = bowler, options = teamBPlayers) { bowler = it }
            }
        },
        confirmButton = {
            Button(onClick = { onConfirm(striker, nonStriker, bowler) }) { Text("Let's Play!") }
        },
        dismissButton = { TextButton(onClick = onDismiss) { Text("Cancel") } }
    )
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DropdownSelector(label: String, selected: String, options: List<String>, onSelect: (String) -> Unit) {
    var expanded by remember { mutableStateOf(false) }
    ExposedDropdownMenuBox(expanded = expanded, onExpandedChange = { expanded = it }) {
        OutlinedTextField(
            value = selected,
            onValueChange = {},
            label = { Text(label) },
            readOnly = true,
            trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = expanded) },
            modifier = Modifier.fillMaxWidth().menuAnchor(MenuAnchorType.PrimaryNotEditable, true)
        )
        ExposedDropdownMenu(expanded = expanded, onDismissRequest = { expanded = false }) {
            options.forEach { option ->
                DropdownMenuItem(text = { Text(option) }, onClick = { onSelect(option); expanded = false })
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TeamCard(
    teamName: String,
    players: List<String>,
    inputValue: String,
    onInputChange: (String) -> Unit,
    onAdd: () -> Unit,
    onRemove: (Int) -> Unit,
    suggestions: List<String>
) {
    var expanded by remember { mutableStateOf(false) }
    val filteredSuggestions = if (inputValue.isNotEmpty()) {
        suggestions.filter { it.contains(inputValue, ignoreCase = true) && it.lowercase() != inputValue.lowercase() }
    } else emptyList()

    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        border = CardDefaults.outlinedCardBorder()
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                Text(text = teamName, fontWeight = FontWeight.Bold, fontSize = 16.sp)
                Surface(color = Color(0xFF1E3A8A), shape = RoundedCornerShape(12.dp)) {
                    Text(text = "${players.size}/11", modifier = Modifier.padding(horizontal = 10.dp, vertical = 4.dp), color = Color.White, fontSize = 12.sp)
                }
            }
            Spacer(Modifier.height(16.dp))
            Row(verticalAlignment = Alignment.CenterVertically) {
                Box(modifier = Modifier.weight(1f)) {
                    ExposedDropdownMenuBox(expanded = expanded && filteredSuggestions.isNotEmpty(), onExpandedChange = { expanded = it }) {
                        OutlinedTextField(
                            value = inputValue,
                            onValueChange = { onInputChange(it); expanded = true },
                            placeholder = { Text("Player name", fontSize = 14.sp) },
                            modifier = Modifier.fillMaxWidth().menuAnchor(MenuAnchorType.PrimaryEditable, true),
                            shape = RoundedCornerShape(12.dp)
                        )
                        if (filteredSuggestions.isNotEmpty()) {
                            ExposedDropdownMenu(expanded = expanded, onDismissRequest = { expanded = false }) {
                                filteredSuggestions.forEach { suggestion ->
                                    DropdownMenuItem(text = { Text(suggestion) }, onClick = { onInputChange(suggestion); expanded = false })
                                }
                            }
                        }
                    }
                }
                Spacer(Modifier.width(8.dp))
                IconButton(onClick = onAdd, modifier = Modifier.background(Color(0xFF1E40AF), RoundedCornerShape(12.dp)).size(48.dp)) {
                    Icon(Icons.Default.Add, null, tint = Color.White)
                }
            }
            Spacer(Modifier.height(12.dp))
            players.forEachIndexed { index, name ->
                PlayerRowItem(index = index + 1, name = name, onRemove = { onRemove(index) })
                Spacer(Modifier.height(4.dp))
            }
        }
    }
}

@Composable
fun PlayerRowItem(index: Int, name: String, onRemove: () -> Unit) {
    Surface(modifier = Modifier.fillMaxWidth(), color = Color(0xFFF8FAFC), shape = RoundedCornerShape(8.dp)) {
        Row(modifier = Modifier.padding(12.dp), horizontalArrangement = Arrangement.SpaceBetween) {
            Text(text = "$index. $name", fontSize = 14.sp)
            Icon(Icons.Default.Close, null, tint = Color.Red, modifier = Modifier.size(18.dp).clickable { onRemove() })
        }
    }
}
