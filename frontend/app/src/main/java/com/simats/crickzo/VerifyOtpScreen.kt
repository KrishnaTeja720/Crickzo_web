package com.simats.crickzo

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Shield
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.key.Key
import androidx.compose.ui.input.key.key
import androidx.compose.ui.input.key.onKeyEvent
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.simats.crickzo.ui.theme.*
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

@Composable
fun VerifyOtpScreen(
    email: String,
    subtitle: String = "Complete Your Registration",
    onBack: () -> Unit,
    onVerifySuccess: (String) -> Unit
) {
    val coroutineScope = rememberCoroutineScope()
    val apiService = RetrofitClient.apiService
    val snackbarHostState = remember { SnackbarHostState() }

    val otpValues = remember { mutableStateListOf("", "", "", "", "", "") }
    val focusRequesters = remember { List(6) { FocusRequester() } }
    
    var isLoading by remember { mutableStateOf(false) }
    var timerSeconds by remember { mutableIntStateOf(58) }

    LaunchedEffect(Unit) {
        while (timerSeconds > 0) {
            delay(1000)
            timerSeconds--
        }
    }

    fun handleVerify() {
        val otp = otpValues.joinToString("")
        if (otp.length < 6) {
            coroutineScope.launch { snackbarHostState.showSnackbar("Please enter all 6 digits") }
            return
        }

        isLoading = true
        coroutineScope.launch {
            try {
                val request = VerifyOtpRequest(email, otp)
                val response = apiService.verifyOtp(request)
                if (response.isSuccessful && response.body()?.status == "verified") {
                    onVerifySuccess(otp)
                } else {
                    snackbarHostState.showSnackbar("Invalid OTP")
                }
            } catch (e: Exception) {
                snackbarHostState.showSnackbar("Connection error: ${e.localizedMessage}")
            } finally {
                isLoading = false
            }
        }
    }

    fun handleResend() {
        if (timerSeconds > 0) return
        
        coroutineScope.launch {
            try {
                val request = ResendOtpRequest(email)
                val response = apiService.resendOtp(request)
                if (response.isSuccessful) {
                    snackbarHostState.showSnackbar("OTP resent successfully")
                    timerSeconds = 58
                } else {
                    snackbarHostState.showSnackbar("Failed to resend OTP")
                }
            } catch (e: Exception) {
                snackbarHostState.showSnackbar("Error: ${e.localizedMessage}")
            }
        }
    }

    Scaffold(
        snackbarHost = { SnackbarHost(snackbarHostState) }
    ) { padding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(
                    brush = Brush.verticalGradient(
                        colors = listOf(BgGradientStart, BgGradientEnd)
                    )
                )
                .padding(padding)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .verticalScroll(rememberScrollState())
                    .padding(horizontal = 24.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Spacer(modifier = Modifier.height(48.dp))

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back", tint = Color.White)
                    }
                    Text(text = "Back", color = Color.White, fontSize = 16.sp)
                }

                Spacer(modifier = Modifier.height(16.dp))

                Surface(
                    modifier = Modifier.size(80.dp),
                    shape = CircleShape,
                    color = Color.White.copy(alpha = 0.2f)
                ) {
                    Icon(
                        imageVector = Icons.Default.Shield,
                        contentDescription = null,
                        tint = Color.White,
                        modifier = Modifier.padding(20.dp).fillMaxSize()
                    )
                }

                Spacer(modifier = Modifier.height(16.dp))

                Text(text = "Verify OTP", color = Color.White, fontSize = 32.sp, fontWeight = FontWeight.Bold)
                Text(text = subtitle, color = Color.White.copy(alpha = 0.8f), fontSize = 16.sp)

                Spacer(modifier = Modifier.height(32.dp))

                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(24.dp),
                    colors = CardDefaults.cardColors(containerColor = Color.White)
                ) {
                    Column(
                        modifier = Modifier.padding(24.dp).fillMaxWidth(),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Text(text = "Enter Verification Code", fontSize = 20.sp, fontWeight = FontWeight.Bold, color = Color.Black)
                        Text(text = "We've sent a 6-digit code to", fontSize = 14.sp, color = GrayText, modifier = Modifier.padding(top = 8.dp))
                        Text(text = email, fontSize = 14.sp, fontWeight = FontWeight.Bold, color = Color.Black)

                        Spacer(modifier = Modifier.height(32.dp))

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            otpValues.forEachIndexed { index, value ->
                                OutlinedTextField(
                                    value = value,
                                    onValueChange = { newVal ->
                                        if (newVal.length <= 1) {
                                            otpValues[index] = newVal
                                            if (newVal.isNotEmpty() && index < 5) {
                                                focusRequesters[index + 1].requestFocus()
                                            }
                                        }
                                    },
                                    modifier = Modifier
                                        .width(44.dp)
                                        .height(56.dp)
                                        .focusRequester(focusRequesters[index])
                                        .onKeyEvent {
                                            if (it.key == Key.Backspace && value.isEmpty() && index > 0) {
                                                focusRequesters[index - 1].requestFocus()
                                                true
                                            } else false
                                        },
                                    textStyle = LocalTextStyle.current.copy(
                                        textAlign = TextAlign.Center,
                                        fontSize = 18.sp,
                                        fontWeight = FontWeight.Bold
                                    ),
                                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                                    shape = RoundedCornerShape(12.dp),
                                    singleLine = true,
                                    colors = OutlinedTextFieldDefaults.colors(
                                        unfocusedBorderColor = Color(0xFFE5E7EB),
                                        focusedBorderColor = PrimaryBlue
                                    )
                                )
                            }
                        }

                        Spacer(modifier = Modifier.height(24.dp))

                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text(text = if (timerSeconds > 0) "Resend code in " else "Didn't receive code? ", color = GrayText, fontSize = 14.sp)
                            if (timerSeconds > 0) {
                                Text(text = "${timerSeconds}s", color = Color.Black, fontSize = 14.sp, fontWeight = FontWeight.Bold)
                            } else {
                                TextButton(onClick = { handleResend() }, contentPadding = PaddingValues(0.dp)) {
                                    Text(text = "Resend", color = LinkBlue, fontSize = 14.sp, fontWeight = FontWeight.Bold)
                                }
                            }
                        }

                        Spacer(modifier = Modifier.height(24.dp))

                        Button(
                            onClick = { handleVerify() },
                            modifier = Modifier.fillMaxWidth().height(56.dp),
                            enabled = !isLoading,
                            shape = RoundedCornerShape(12.dp),
                            colors = ButtonDefaults.buttonColors(containerColor = PrimaryBlue)
                        ) {
                            if (isLoading) {
                                CircularProgressIndicator(color = Color.White, modifier = Modifier.size(24.dp))
                            } else {
                                Icon(Icons.Default.CheckCircle, contentDescription = null, modifier = Modifier.size(18.dp))
                                Spacer(modifier = Modifier.width(8.dp))
                                Text(text = "Verify & Continue", fontSize = 16.sp, fontWeight = FontWeight.Bold)
                            }
                        }

                        Spacer(modifier = Modifier.height(24.dp))

                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .background(Color(0xFFEFF6FF), RoundedCornerShape(12.dp))
                                .border(1.dp, Color(0xFFDBEAFE), RoundedCornerShape(12.dp))
                                .padding(16.dp)
                        ) {
                            Text(
                                text = "Didn't receive the code? Check your spam folder or click resend",
                                color = Color(0xFF1E40AF),
                                fontSize = 12.sp,
                                textAlign = TextAlign.Center
                            )
                        }
                    }
                }

                Spacer(modifier = Modifier.height(32.dp))

                Text(
                    text = "The verification code will expire in 10 minutes",
                    color = Color.White.copy(alpha = 0.7f),
                    fontSize = 12.sp,
                    modifier = Modifier.padding(bottom = 32.dp)
                )
            }
        }
    }
}
