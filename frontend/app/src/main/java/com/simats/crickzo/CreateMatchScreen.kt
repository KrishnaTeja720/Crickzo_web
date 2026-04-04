package com.simats.crickzo

import android.content.Context
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.ArrowForward
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.KeyboardArrowDown
import androidx.compose.material.icons.filled.KeyboardArrowUp
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

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CreateMatchScreen(onBack: () -> Unit, onContinue: (Int, String, String) -> Unit) {
    val coroutineScope = rememberCoroutineScope()
    val apiService = RetrofitClient.apiService
    val snackbarHostState = remember { SnackbarHostState() }
    val context = LocalContext.current

    var matchFormat by remember { mutableStateOf("T20 (20 overs)") }
    var otherFormat by remember { mutableStateOf("") }
    var teamAName by remember { mutableStateOf("") }
    var teamBName by remember { mutableStateOf("") }
    var venue by remember { mutableStateOf("") }
    var showAdvancedOptions by remember { mutableStateOf(false) }
    
    var tossWinner by remember { mutableStateOf("Team A") }
    var pitchType by remember { mutableStateOf("Balanced") }
    var weatherConditions by remember { mutableStateOf("Normal") }

    var isCreating by remember { mutableStateOf(false) }

    val isContinueEnabled = teamAName.isNotBlank() && teamBName.isNotBlank() && (matchFormat != "Others" || otherFormat.isNotBlank()) && !isCreating

    fun handleCreateMatch() {
        val sharedPrefs = context.getSharedPreferences("crickzo_prefs", Context.MODE_PRIVATE)
        val userId = sharedPrefs.getInt("user_id", -1)

        if (userId <= 0) {
            coroutineScope.launch {
                snackbarHostState.showSnackbar("User not logged in")
            }
            return
        }

        isCreating = true
        coroutineScope.launch {
            try {
                val formatToSend = if (matchFormat == "Others") otherFormat else matchFormat
                val request = CreateMatchRequest(
                    user_id = userId,
                    team_a = teamAName,
                    team_b = teamBName,
                    format = formatToSend,
                    venue = venue,
                    toss = if (tossWinner == "Team A") teamAName else teamBName,
                    pitch = pitchType,
                    weather = weatherConditions
                )
                
                val response = apiService.createMatch(request)
                if (response.isSuccessful) {
                    val responseBody = response.body()
                    if (responseBody != null && responseBody.status == "success") {
                        val matchId = responseBody.matchId
                        onContinue(matchId, teamAName, teamBName)
                    } else {
                        snackbarHostState.showSnackbar("Error: ${responseBody?.message ?: "Unknown error"}")
                    }
                } else {
                    snackbarHostState.showSnackbar("Error: ${response.message()}")
                }
            } catch (e: Exception) {
                snackbarHostState.showSnackbar("Network error: ${e.localizedMessage}")
            } finally {
                isCreating = false
            }
        }
    }

    val teamSuggestions = listOf(
        "Mumbai Indians", "Chennai Super Kings", "Royal Challengers Bangalore",
        "Kolkata Knight Riders", "Delhi Capitals", "Punjab Kings",
        "Rajasthan Royals", "Sunrisers Hyderabad", "Gujarat Titans",
        "Lucknow Super Giants", "India", "Australia", "England"
    ).sorted()

    Scaffold(
        snackbarHost = { SnackbarHost(snackbarHostState) },
        topBar = {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(Color(0xFF1E40AF))
                    .padding(top = 40.dp, bottom = 20.dp, start = 16.dp, end = 16.dp)
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    IconButton(onClick = onBack) {
                        Icon(imageVector = Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back", tint = Color.White)
                    }
                    Spacer(modifier = Modifier.width(12.dp))
                    Column {
                        Text(text = "Create New Match", color = Color.White, fontSize = 18.sp, fontWeight = FontWeight.Bold)
                        Text(text = "Step 1 of 2: Match Details", color = Color.White.copy(alpha = 0.8f), fontSize = 12.sp)
                    }
                }
            }
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .background(Color(0xFFF8FAFC))
                .verticalScroll(rememberScrollState())
                .padding(innerPadding)
                .padding(20.dp)
        ) {
            // Main Details Card
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = Color.White),
                border = CardDefaults.outlinedCardBorder()
            ) {
                Column(modifier = Modifier.padding(20.dp)) {
                    MatchDropdownField(
                        label = "Match Format *",
                        value = matchFormat,
                        onValueChange = { 
                            matchFormat = it 
                            if (it != "Others") otherFormat = ""
                        },
                        placeholder = "Select format",
                        options = listOf("T20 (20 overs)", "ODI (50 overs)", "Test (unlimited overs)", "Others")
                    )
                    
                    if (matchFormat == "Others") {
                        Spacer(modifier = Modifier.height(16.dp))
                        CreateMatchField(
                            label = "Specify Match Format *",
                            value = otherFormat,
                            onValueChange = { otherFormat = it },
                            placeholder = "e.g., 5-over match"
                        )
                    }

                    Spacer(modifier = Modifier.height(20.dp))
                    
                    FieldWithSuggestions(
                        label = "Team A Name *",
                        value = teamAName,
                        onValueChange = { teamAName = it },
                        placeholder = "e.g., Mumbai Indians",
                        suggestions = teamSuggestions
                    )
                    
                    Spacer(modifier = Modifier.height(20.dp))
                    
                    FieldWithSuggestions(
                        label = "Team B Name *",
                        value = teamBName,
                        onValueChange = { teamBName = it },
                        placeholder = "e.g., Chennai Super Kings",
                        suggestions = teamSuggestions
                    )

                    Spacer(modifier = Modifier.height(20.dp))
                    CreateMatchField(
                        label = "Venue (Optional)",
                        value = venue,
                        onValueChange = { venue = it },
                        placeholder = "e.g., Wankhede Stadium"
                    )
                }
            }

            Spacer(modifier = Modifier.height(20.dp))

            // Advanced Options Card
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = Color.White),
                border = CardDefaults.outlinedCardBorder()
            ) {
                Column(modifier = Modifier.padding(20.dp)) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clickable { showAdvancedOptions = !showAdvancedOptions },
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(text = "Advanced Options (Optional)", fontSize = 16.sp, fontWeight = FontWeight.Bold, color = Color(0xFF1E293B))
                        Icon(imageVector = if (showAdvancedOptions) Icons.Default.KeyboardArrowUp else Icons.Default.KeyboardArrowDown, contentDescription = null)
                    }

                    AnimatedVisibility(visible = showAdvancedOptions) {
                        Column(modifier = Modifier.padding(top = 20.dp)) {
                            MatchDropdownField(
                                label = "Toss Winner",
                                value = tossWinner,
                                onValueChange = { tossWinner = it },
                                placeholder = "Select toss winner",
                                options = listOf("Team A", "Team B")
                            )
                            Spacer(modifier = Modifier.height(16.dp))
                            MatchDropdownField(
                                label = "Pitch Type",
                                value = pitchType,
                                onValueChange = { pitchType = it },
                                placeholder = "Select pitch type",
                                options = listOf("Batting Friendly", "Balanced", "Bowling Friendly")
                            )
                            Spacer(modifier = Modifier.height(16.dp))
                            MatchDropdownField(
                                label = "Weather Conditions",
                                value = weatherConditions,
                                onValueChange = { weatherConditions = it },
                                placeholder = "Select weather",
                                options = listOf("Normal", "Humid", "Rain Chance")
                            )
                        }
                    }
                }
            }

            Spacer(modifier = Modifier.height(32.dp))

            Button(
                onClick = { handleCreateMatch() },
                enabled = isContinueEnabled,
                modifier = Modifier.fillMaxWidth().height(56.dp),
                shape = RoundedCornerShape(12.dp),
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF1E40AF))
            ) {
                if (isCreating) {
                    CircularProgressIndicator(color = Color.White, modifier = Modifier.size(24.dp))
                } else {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(text = "Continue to Add Players", fontSize = 16.sp, fontWeight = FontWeight.Bold)
                        Spacer(modifier = Modifier.width(8.dp))
                        Icon(imageVector = Icons.AutoMirrored.Filled.ArrowForward, contentDescription = null, modifier = Modifier.size(18.dp))
                    }
                }
            }

            Spacer(modifier = Modifier.height(40.dp))
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun FieldWithSuggestions(
    label: String,
    value: String,
    onValueChange: (String) -> Unit,
    placeholder: String,
    suggestions: List<String>
) {
    var expanded by remember { mutableStateOf(false) }
    val filteredSuggestions = if (value.isNotEmpty()) {
        suggestions.filter { it.contains(value, ignoreCase = true) && it.lowercase() != value.lowercase() }
    } else emptyList()

    Column {
        Text(text = label, fontSize = 14.sp, fontWeight = FontWeight.Bold, color = Color(0xFF1E293B))
        Spacer(modifier = Modifier.height(8.dp))
        ExposedDropdownMenuBox(
            expanded = expanded && filteredSuggestions.isNotEmpty(),
            onExpandedChange = { expanded = it },
            modifier = Modifier.fillMaxWidth()
        ) {
            OutlinedTextField(
                value = value,
                onValueChange = { onValueChange(it); expanded = true },
                modifier = Modifier.fillMaxWidth().menuAnchor(MenuAnchorType.PrimaryEditable, true),
                placeholder = { Text(placeholder, color = Color(0xFF94A3B8), fontSize = 14.sp) },
                shape = RoundedCornerShape(12.dp),
                colors = OutlinedTextFieldDefaults.colors(
                    focusedBorderColor = Color(0xFF1E40AF),
                    unfocusedBorderColor = Color(0xFFF1F5F9),
                    focusedContainerColor = Color(0xFFF8FAFC),
                    unfocusedContainerColor = Color(0xFFF8FAFC)
                ),
                singleLine = true
            )

            if (filteredSuggestions.isNotEmpty()) {
                ExposedDropdownMenu(
                    expanded = expanded,
                    onDismissRequest = { expanded = false },
                    modifier = Modifier.background(Color.White)
                ) {
                    filteredSuggestions.forEach { suggestion ->
                        DropdownMenuItem(
                            text = { Text(suggestion, fontSize = 14.sp) },
                            onClick = { onValueChange(suggestion); expanded = false },
                            contentPadding = ExposedDropdownMenuDefaults.ItemContentPadding
                        )
                    }
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MatchDropdownField(
    label: String,
    value: String,
    onValueChange: (String) -> Unit,
    placeholder: String,
    options: List<String>
) {
    var expanded by remember { mutableStateOf(false) }

    Column {
        Text(text = label, fontSize = 14.sp, fontWeight = FontWeight.Bold, color = Color(0xFF1E293B))
        Spacer(modifier = Modifier.height(8.dp))
        ExposedDropdownMenuBox(
            expanded = expanded,
            onExpandedChange = { expanded = it },
            modifier = Modifier.fillMaxWidth()
        ) {
            OutlinedTextField(
                value = value,
                onValueChange = {},
                modifier = Modifier.fillMaxWidth().menuAnchor(MenuAnchorType.PrimaryNotEditable, true),
                readOnly = true,
                placeholder = { Text(placeholder, color = Color(0xFF94A3B8), fontSize = 14.sp) },
                trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = expanded) },
                shape = RoundedCornerShape(12.dp),
                colors = OutlinedTextFieldDefaults.colors(
                    focusedBorderColor = Color(0xFF1E40AF),
                    unfocusedBorderColor = Color(0xFFF1F5F9),
                    focusedContainerColor = Color(0xFFF8FAFC),
                    unfocusedContainerColor = Color(0xFFF8FAFC)
                )
            )

            ExposedDropdownMenu(
                expanded = expanded,
                onDismissRequest = { expanded = false },
                modifier = Modifier.background(Color.White)
            ) {
                options.forEach { option ->
                    DropdownMenuItem(
                        text = {
                            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                                Text(text = option, fontSize = 14.sp)
                                if (option == value) Icon(Icons.Default.Check, null, tint = Color(0xFF1E40AF), modifier = Modifier.size(18.dp))
                            }
                        },
                        onClick = { onValueChange(option); expanded = false },
                        contentPadding = ExposedDropdownMenuDefaults.ItemContentPadding
                    )
                }
            }
        }
    }
}

@Composable
fun CreateMatchField(
    label: String,
    value: String,
    onValueChange: (String) -> Unit,
    placeholder: String
) {
    Column {
        Text(text = label, fontSize = 14.sp, fontWeight = FontWeight.Bold, color = Color(0xFF1E293B))
        Spacer(modifier = Modifier.height(8.dp))
        OutlinedTextField(
            value = value,
            onValueChange = onValueChange,
            modifier = Modifier.fillMaxWidth(),
            placeholder = { Text(placeholder, color = Color(0xFF94A3B8), fontSize = 14.sp) },
            shape = RoundedCornerShape(12.dp),
            colors = OutlinedTextFieldDefaults.colors(
                focusedBorderColor = Color(0xFF1E40AF),
                unfocusedBorderColor = Color(0xFFF1F5F9),
                focusedContainerColor = Color(0xFFF8FAFC),
                unfocusedContainerColor = Color(0xFFF8FAFC)
            ),
            singleLine = true
        )
    }
}
