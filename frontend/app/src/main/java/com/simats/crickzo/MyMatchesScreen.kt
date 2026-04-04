package com.simats.crickzo

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Bolt
import androidx.compose.material.icons.filled.EmojiEvents
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material3.*
import androidx.compose.material3.TabRowDefaults.tabIndicatorOffset
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.simats.crickzo.ui.theme.GrayText

@Composable
fun MyMatchesScreen(
    matches: List<CreatedMatch>,
    completedMatches: List<CompletedMatchInfo>,
    initialTab: String = "Live",
    onBack: () -> Unit,
    onScoreMatch: (CreatedMatch) -> Unit,
    onCompletedMatchClick: (CompletedMatchInfo) -> Unit = {},
    onAddMatch: () -> Unit = {}
) {
    var selectedTab by remember { mutableStateOf(initialTab) }
    val tabs = listOf("Live", "Upcoming", "Completed")

    // Update selectedTab if initialTab changes (useful when navigating from Home)
    LaunchedEffect(initialTab) {
        selectedTab = initialTab
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFFF8FAFC))
    ) {
        // Header
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .background(Color(0xFF1E40AF))
                .padding(top = 40.dp, bottom = 16.dp)
        ) {
            Column {
                Row(
                    modifier = Modifier.fillMaxWidth().padding(horizontal = 8.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    IconButton(onClick = onBack) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = "Back",
                            tint = Color.White
                        )
                    }
                    Text(
                        text = "My Matches",
                        color = Color.White,
                        fontSize = 20.sp,
                        fontWeight = FontWeight.Bold
                    )
                }
                
                Spacer(modifier = Modifier.height(16.dp))
                
                // Tab Row
                ScrollableTabRow(
                    selectedTabIndex = tabs.indexOf(selectedTab).coerceAtLeast(0),
                    containerColor = Color.Transparent,
                    contentColor = Color.White,
                    edgePadding = 16.dp,
                    divider = {},
                    indicator = { tabPositions ->
                        val index = tabs.indexOf(selectedTab).coerceAtLeast(0)
                        TabRowDefaults.SecondaryIndicator(
                            modifier = Modifier.tabIndicatorOffset(tabPositions[index]),
                            color = Color.White
                        )
                    }
                ) {
                    tabs.forEach { tab ->
                        Tab(
                            selected = selectedTab == tab,
                            onClick = { selectedTab = tab },
                            text = { 
                                Text(
                                    text = tab,
                                    fontSize = 14.sp,
                                    fontWeight = if (selectedTab == tab) FontWeight.Bold else FontWeight.Normal
                                )
                            }
                        )
                    }
                }
            }
        }

        val currentMatches = when (selectedTab) {
            "Live" -> matches.filter { it.status == "LIVE" }
            "Upcoming" -> matches.filter { it.status == "UPCOMING" }
            else -> listOf()
        }

        if (selectedTab == "Completed") {
            if (completedMatches.isEmpty()) {
                EmptyState(onAddMatch, "No completed matches yet")
            } else {
                LazyColumn(
                    modifier = Modifier.fillMaxSize(),
                    contentPadding = PaddingValues(16.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    items(completedMatches) { match ->
                        CompletedMatchCard(match = match, onClick = { onCompletedMatchClick(match) })
                    }
                }
            }
        } else {
            if (currentMatches.isEmpty()) {
                EmptyState(onAddMatch, "No $selectedTab matches found")
            } else {
                LazyColumn(
                    modifier = Modifier.fillMaxSize(),
                    contentPadding = PaddingValues(16.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    items(currentMatches) { match ->
                        MyMatchCard(match = match, onScoreClick = { onScoreMatch(match) })
                    }
                }
            }
        }
    }
}

@Composable
fun EmptyState(onAddMatch: () -> Unit, message: String) {
    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            modifier = Modifier.padding(24.dp)
        ) {
            Surface(
                modifier = Modifier.size(80.dp),
                shape = CircleShape,
                color = Color(0xFFEFF6FF)
            ) {
                Box(contentAlignment = Alignment.Center) {
                    Icon(
                        imageVector = Icons.Default.Add,
                        contentDescription = null,
                        tint = Color(0xFF1E40AF),
                        modifier = Modifier.size(40.dp)
                    )
                }
            }
            Spacer(Modifier.height(24.dp))
            Text(
                text = "No matches found",
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold,
                color = Color(0xFF1E293B)
            )
            Spacer(Modifier.height(8.dp))
            Text(
                text = message,
                fontSize = 14.sp,
                color = Color(0xFF64748B),
                textAlign = TextAlign.Center
            )
            Spacer(Modifier.height(32.dp))
            Button(
                onClick = onAddMatch,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(56.dp),
                shape = RoundedCornerShape(12.dp),
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF1E40AF))
            ) {
                Icon(Icons.Default.Add, contentDescription = null)
                Spacer(Modifier.width(8.dp))
                Text(text = "Add New Match", fontSize = 16.sp, fontWeight = FontWeight.Bold)
            }
        }
    }
}

@Composable
fun MyMatchCard(match: CreatedMatch, onScoreClick: () -> Unit) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        elevation = CardDefaults.cardElevation(defaultElevation = 0.dp),
        border = CardDefaults.outlinedCardBorder()
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    if (match.status == "LIVE") {
                        Surface(
                            color = Color(0xFFFFE4E6),
                            shape = RoundedCornerShape(12.dp)
                        ) {
                            Row(
                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Box(modifier = Modifier.size(6.dp).background(Color(0xFFEF4444), CircleShape))
                                Spacer(Modifier.width(4.dp))
                                Text(text = "LIVE", color = Color(0xFFEF4444), fontSize = 10.sp, fontWeight = FontWeight.Bold)
                            }
                        }
                        Spacer(Modifier.width(8.dp))
                    }
                    
                    Surface(
                        color = Color(0xFFEFF6FF),
                        shape = RoundedCornerShape(12.dp)
                    ) {
                        Text(
                            text = match.type,
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                            color = Color(0xFF1E40AF),
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Bold
                        )
                    }
                }
                
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Default.LocationOn, contentDescription = null, modifier = Modifier.size(14.dp), tint = GrayText)
                    Text(text = match.location, color = GrayText, fontSize = 12.sp)
                }
            }

            Spacer(Modifier.height(16.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Surface(modifier = Modifier.size(48.dp), shape = CircleShape, color = Color(0xFFF1F5F9)) {
                        Box(contentAlignment = Alignment.Center) {
                            Text(text = match.teamA.take(1), fontWeight = FontWeight.Bold, color = Color(0xFF1E40AF))
                        }
                    }
                    Spacer(Modifier.height(8.dp))
                    Text(text = match.teamA, fontWeight = FontWeight.Bold, fontSize = 14.sp)
                }

                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text(text = "VS", color = Color(0xFF94A3B8), fontWeight = FontWeight.Bold, fontSize = 14.sp)
                }

                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Surface(modifier = Modifier.size(48.dp), shape = CircleShape, color = Color(0xFFF1F5F9)) {
                        Box(contentAlignment = Alignment.Center) {
                            Text(text = match.teamB.take(1), fontWeight = FontWeight.Bold, color = Color(0xFF1E40AF))
                        }
                    }
                    Spacer(Modifier.height(8.dp))
                    Text(text = match.teamB, fontWeight = FontWeight.Bold, fontSize = 14.sp)
                }
            }

            Spacer(Modifier.height(24.dp))

            Button(
                onClick = onScoreClick,
                modifier = Modifier.fillMaxWidth().height(48.dp),
                shape = RoundedCornerShape(12.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = if (match.status == "LIVE") Color(0xFF1E40AF) else Color(0xFFF1F5F9),
                    contentColor = if (match.status == "LIVE") Color.White else Color(0xFF1E40AF)
                )
            ) {
                if (match.status == "LIVE") {
                    Icon(Icons.Default.Bolt, contentDescription = null, modifier = Modifier.size(18.dp))
                    Spacer(Modifier.width(8.dp))
                }
                Text(
                    text = if (match.status == "LIVE") "Score Now" else "Match Details",
                    fontWeight = FontWeight.Bold
                )
            }
        }
    }
}
