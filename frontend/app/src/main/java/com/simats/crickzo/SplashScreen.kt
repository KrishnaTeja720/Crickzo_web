package com.simats.crickzo

import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowForward
import androidx.compose.material.icons.filled.Bolt
import androidx.compose.material.icons.filled.SportsCricket
import androidx.compose.material.icons.filled.TrendingUp
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
import kotlinx.coroutines.delay

@Composable
fun MainSplashScreen(onFinished: () -> Unit) {
    var currentStep by remember { mutableStateOf(0) }

    LaunchedEffect(currentStep) {
        if (currentStep == 0) {
            delay(2000)
            currentStep = 1
        }
    }

    Box(modifier = Modifier.fillMaxSize()) {
        when (currentStep) {
            0 -> SplashScreenContent()
            1 -> OnboardingScreen(
                title = "Final Score Prediction",
                description = "Get real-time cricket final score predictions based on current match conditions.",
                icon = Icons.Default.Bolt,
                step = 1,
                onNext = { currentStep = 2 },
                onSkip = onFinished
            )
            2 -> OnboardingScreen(
                title = "Win Probability Forecasting",
                description = "Advanced analytics providing win probability predictions.",
                icon = Icons.Default.TrendingUp,
                step = 2,
                onNext = onFinished,
                onSkip = onFinished
            )
        }
    }
}

@Composable
fun SplashScreenContent() {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFF1E40AF)),
        contentAlignment = Alignment.Center
    ) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Surface(
                modifier = Modifier.size(140.dp),
                shape = CircleShape,
                color = Color.White
            ) {
                Box(contentAlignment = Alignment.Center) {
                    Icon(
                        imageVector = Icons.Default.SportsCricket,
                        contentDescription = null,
                        tint = Color(0xFF1E40AF),
                        modifier = Modifier.size(60.dp)
                    )
                }
            }
            Spacer(modifier = Modifier.height(32.dp))
            Text(
                text = "crickzo",
                color = Color.White,
                fontSize = 48.sp,
                fontWeight = FontWeight.ExtraBold
            )
            Text(
                text = "Powered by Intelligence",
                color = Color.White.copy(alpha = 0.9f),
                fontSize = 16.sp,
                fontWeight = FontWeight.Medium
            )
        }
        
        Text(
            text = "powered by SIMATS Engineering",
            color = Color.White.copy(alpha = 0.5f),
            fontSize = 12.sp,
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .padding(bottom = 40.dp)
        )
    }
}

@Composable
fun OnboardingScreen(
    title: String,
    description: String,
    icon: ImageVector,
    step: Int,
    onNext: () -> Unit,
    onSkip: () -> Unit
) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFF1E40AF))
    ) {
        Text(
            text = "Skip",
            color = Color.White.copy(alpha = 0.7f),
            modifier = Modifier
                .align(Alignment.TopEnd)
                .padding(top = 48.dp, end = 24.dp)
                .clickable { onSkip() },
            fontSize = 14.sp
        )

        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(horizontal = 40.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Surface(
                modifier = Modifier.size(120.dp),
                shape = RoundedCornerShape(32.dp),
                color = Color.White
            ) {
                Box(contentAlignment = Alignment.Center) {
                    Icon(
                        imageVector = icon,
                        contentDescription = null,
                        tint = Color(0xFF1E40AF),
                        modifier = Modifier.size(56.dp)
                    )
                }
            }

            Spacer(modifier = Modifier.height(48.dp))

            Text(
                text = title,
                color = Color.White,
                fontSize = 28.sp,
                fontWeight = FontWeight.Bold,
                textAlign = TextAlign.Center,
                lineHeight = 36.sp
            )

            Spacer(modifier = Modifier.height(24.dp))

            Text(
                text = description,
                color = Color.White.copy(alpha = 0.8f),
                fontSize = 16.sp,
                textAlign = TextAlign.Center,
                lineHeight = 24.sp
            )

            Spacer(modifier = Modifier.height(40.dp))

            // Step Indicator
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Box(
                    modifier = Modifier
                        .width(if (step == 1) 24.dp else 8.dp)
                        .height(4.dp)
                        .background(
                            if (step == 1) Color.White else Color.White.copy(alpha = 0.3f),
                            CircleShape
                        )
                )
                Box(
                    modifier = Modifier
                        .width(if (step == 2) 24.dp else 8.dp)
                        .height(4.dp)
                        .background(
                            if (step == 2) Color.White else Color.White.copy(alpha = 0.3f),
                            CircleShape
                        )
                )
            }

            Spacer(modifier = Modifier.height(48.dp))

            Button(
                onClick = onNext,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(56.dp),
                colors = ButtonDefaults.buttonColors(containerColor = Color.White),
                shape = RoundedCornerShape(16.dp)
            ) {
                Text(
                    text = if (step == 1) "Next" else "Get Started",
                    color = Color(0xFF1E40AF),
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.width(8.dp))
                Icon(
                    imageVector = Icons.AutoMirrored.Filled.ArrowForward,
                    contentDescription = null,
                    tint = Color(0xFF1E40AF),
                    modifier = Modifier.size(20.dp)
                )
            }
        }

        Text(
            text = "powered by SIMATS Engineering",
            color = Color.White.copy(alpha = 0.5f),
            fontSize = 12.sp,
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .padding(bottom = 40.dp)
        )
    }
}
