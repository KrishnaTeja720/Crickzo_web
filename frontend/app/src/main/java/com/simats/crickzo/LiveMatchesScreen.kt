package com.simats.crickzo

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material.icons.filled.QueryStats
import androidx.compose.material.icons.filled.Timeline
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.launch

@Composable
fun LiveMatchesScreen(
    userId: Int,
    onBack: () -> Unit,
    onUpdateScore: (LiveMatchData) -> Unit,
    onViewPredictions: (LiveMatchData) -> Unit
) {
    val coroutineScope = rememberCoroutineScope()
    var liveMatches by remember { mutableStateOf(listOf<LiveMatchData>()) }
    var isLoading by remember { mutableStateOf(true) }

    val mockLiveMatches = listOf(
        LiveMatchData(
            matchId = 101,
            teamA = "Mumbai Indians",
            teamB = "Chennai Super Kings",
            venue = "Wankhede Stadium",
            runs = 142,
            wickets = 3,
            overs = 15.2f,
            crr = 9.26f
        ),
        LiveMatchData(
            matchId = 102,
            teamA = "Royal Challengers Bangalore",
            teamB = "Kolkata Knight Riders",
            venue = "M. Chinnaswamy Stadium",
            runs = 98,
            wickets = 2,
            overs = 10.4f,
            crr = 9.19f
        )
    )

    LaunchedEffect(Unit) {
        coroutineScope.launch {
            try {
                val response = RetrofitClient.apiService.getLiveMatches(userId)
                if (response.isSuccessful) {
                    liveMatches = response.body() ?: mockLiveMatches
                } else {
                    liveMatches = mockLiveMatches
                }
            } catch (e: Exception) {
                e.printStackTrace()
                liveMatches = mockLiveMatches
            } finally {
                isLoading = false
            }
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFFF8FAFC))
    ) {
        // Header
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(top = 40.dp, bottom = 16.dp, start = 8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            IconButton(onClick = onBack) {
                Icon(
                    imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                    contentDescription = "Back",
                    tint = Color(0xFF1E40AF)
                )
            }
            Text(
                text = "Live Matches",
                color = Color(0xFF1E40AF),
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold
            )
        }

        if (isLoading) {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator(color = Color(0xFF1E40AF))
            }
        } else if (liveMatches.isEmpty()) {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                Text("No live matches at the moment", color = Color.Gray)
            }
        } else {
            LazyColumn(
                modifier = Modifier.fillMaxSize(),
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                items(liveMatches) { match ->
                    LiveMatchCard(
                        match = match,
                        onUpdateScore = { onUpdateScore(match) },
                        onViewPredictions = { onViewPredictions(match) }
                    )
                }
            }
        }
    }
}

@Composable
fun LiveMatchCard(match: LiveMatchData, onUpdateScore: () -> Unit, onViewPredictions: () -> Unit) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(24.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
        border = CardDefaults.outlinedCardBorder()
    ) {
        Column(modifier = Modifier.padding(20.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Surface(
                        color = Color(0xFFFFE4E6),
                        shape = RoundedCornerShape(12.dp)
                    ) {
                        Row(
                            modifier = Modifier.padding(horizontal = 10.dp, vertical = 4.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Box(modifier = Modifier.size(6.dp).background(Color(0xFFEF4444), CircleShape))
                            Spacer(Modifier.width(6.dp))
                            Text("LIVE", color = Color(0xFFEF4444), fontSize = 12.sp, fontWeight = FontWeight.Bold)
                        }
                    }
                }
                
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Default.LocationOn, contentDescription = null, modifier = Modifier.size(16.dp), tint = Color(0xFF94A3B8))
                    Spacer(Modifier.width(4.dp))
                    Text(text = match.venue ?: "Local Ground", color = Color(0xFF94A3B8), fontSize = 12.sp)
                }
            }

            Spacer(Modifier.height(20.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(modifier = Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Text(text = match.teamA ?: "Team A", fontWeight = FontWeight.Bold, fontSize = 16.sp, color = Color(0xFF1E293B))
                    Text(text = match.teamB ?: "Team B", fontWeight = FontWeight.Bold, fontSize = 16.sp, color = Color(0xFF1E293B))
                }
                Column(horizontalAlignment = Alignment.End, verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Text(text = "${match.runs}/${match.wickets}", fontWeight = FontWeight.Bold, fontSize = 16.sp, color = Color(0xFF1E293B))
                    Text(text = "(${match.overs})", color = Color(0xFF94A3B8), fontSize = 14.sp)
                }
            }

            Spacer(Modifier.height(16.dp))

            Surface(
                modifier = Modifier.fillMaxWidth(),
                color = Color(0xFFEFF6FF).copy(alpha = 0.5f),
                shape = RoundedCornerShape(12.dp)
            ) {
                Row(
                    modifier = Modifier.padding(12.dp),
                    horizontalArrangement = Arrangement.Start,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(text = "CRR ", color = Color(0xFF94A3B8), fontSize = 13.sp)
                    Text(text = match.crr.toString(), fontWeight = FontWeight.Bold, color = Color(0xFF1E40AF), fontSize = 13.sp)
                }
            }

            Spacer(Modifier.height(20.dp))

            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                Button(
                    onClick = onUpdateScore,
                    modifier = Modifier.weight(1f).height(52.dp),
                    shape = RoundedCornerShape(16.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF1E40AF))
                ) {
                    Icon(Icons.Default.Timeline, contentDescription = null, modifier = Modifier.size(20.dp))
                    Spacer(Modifier.width(8.dp))
                    Text("Score", fontWeight = FontWeight.Bold, fontSize = 15.sp)
                }
                
                OutlinedButton(
                    onClick = onViewPredictions,
                    modifier = Modifier.weight(1f).height(52.dp),
                    shape = RoundedCornerShape(16.dp),
                    border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFF1E40AF)),
                    colors = ButtonDefaults.outlinedButtonColors(contentColor = Color(0xFF1E40AF))
                ) {
                    Icon(Icons.Default.QueryStats, contentDescription = null, modifier = Modifier.size(20.dp))
                    Spacer(Modifier.width(8.dp))
                    Text("Predictions", fontWeight = FontWeight.Bold, fontSize = 15.sp)
                }
            }
        }
    }
}
