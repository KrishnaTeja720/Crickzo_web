package com.simats.crickzo

import android.Manifest
import android.content.Context
import android.os.Build
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.runtime.*
import androidx.work.*
import com.simats.crickzo.ui.theme.CrickzoTheme
import kotlinx.coroutines.launch
import java.util.*
import java.util.concurrent.TimeUnit

class MainActivity : ComponentActivity() {
    
    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted: Boolean ->
        if (isGranted) {
            scheduleScoreUpdate()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            requestPermissionLauncher.launch(Manifest.permission.POST_NOTIFICATIONS)
        } else {
            scheduleScoreUpdate()
        }

        val sharedPrefs = getSharedPreferences("crickzo_prefs", Context.MODE_PRIVATE)

        setContent {
            CrickzoTheme {
                val coroutineScope = rememberCoroutineScope()
                val apiService = RetrofitClient.apiService
                
                var currentScreen by remember { mutableStateOf("splash") }
                
                val savedEmail = sharedPrefs.getString("user_email", null)
                val savedName = sharedPrefs.getString("user_name", null)
                val savedUserId = sharedPrefs.getInt("user_id", 0)
                
                var userEmail by remember { mutableStateOf(savedEmail ?: "") }
                var userName by remember { mutableStateOf(savedName ?: "") }
                var userId by remember { mutableIntStateOf(savedUserId) }
                var userOtp by remember { mutableStateOf("") }
                var otpSubtitle by remember { mutableStateOf("Complete Your Registration") }

                when (currentScreen) {
                    "splash" -> {
                        MainSplashScreen(
                            onFinished = { 
                                if (sharedPrefs.getString("user_email", null) != null) {
                                    currentScreen = "home"
                                } else {
                                    currentScreen = "login"
                                }
                            }
                        )
                    }
                    "login" -> {
                        LoginScreen(
                            onSignUpClick = { currentScreen = "signup" },
                            onForgotPasswordClick = { currentScreen = "forgot_password" },
                            onLoginSuccess = { name, email, id ->
                                userName = name
                                userEmail = email
                                userId = id
                                sharedPrefs.edit()
                                    .putString("user_email", email)
                                    .putString("user_name", name)
                                    .putInt("user_id", id)
                                    .apply()
                                currentScreen = "home"
                            }
                        )
                    }
                    "signup" -> {
                        SignUpScreen(
                            onBackToLogin = { currentScreen = "login" },
                            onSignUpSuccess = { email, name ->
                                userEmail = email
                                userName = name
                                otpSubtitle = "Complete Your Registration"
                                
                                // Trigger OTP generation because backend signup doesn't send it automatically
                                coroutineScope.launch {
                                    try {
                                        apiService.resendOtp(ResendOtpRequest(email))
                                    } catch (e: Exception) {
                                        // Silent fail, user can click "Resend" on OTP screen
                                    }
                                }
                                currentScreen = "verify_otp"
                            }
                        )
                    }
                    "forgot_password" -> {
                        ForgotPasswordScreen(
                            onBackToLogin = { currentScreen = "login" },
                            onCodeSent = { email ->
                                userEmail = email
                                otpSubtitle = "Verify Your Identity"
                                currentScreen = "verify_otp"
                            }
                        )
                    }
                    "verify_otp" -> {
                        VerifyOtpScreen(
                            email = userEmail,
                            subtitle = otpSubtitle,
                            onBack = { 
                                if (otpSubtitle == "Verify Your Identity") {
                                    currentScreen = "forgot_password"
                                } else {
                                    currentScreen = "signup"
                                }
                            },
                            onVerifySuccess = { otp ->
                                userOtp = otp
                                if (otpSubtitle == "Verify Your Identity") {
                                    currentScreen = "reset_password"
                                } else {
                                    // Account successfully created and verified
                                    currentScreen = "login"
                                }
                            }
                        )
                    }
                    "reset_password" -> {
                        ResetPasswordScreen(
                            email = userEmail,
                            otp = userOtp,
                            onBack = { currentScreen = "verify_otp" },
                            onResetSuccess = {
                                currentScreen = "login"
                            }
                        )
                    }
                    "home" -> {
                        HomeScreen(
                            userName = userName,
                            userEmail = userEmail,
                            userId = userId,
                            onUpdateProfile = { name, email ->
                                userName = name
                                userEmail = email
                                sharedPrefs.edit()
                                    .putString("user_email", email)
                                    .putString("user_name", name)
                                    .apply()
                            },
                            onLogout = { 
                                sharedPrefs.edit().clear().apply()
                                currentScreen = "login" 
                            }
                        )
                    }
                }
            }
        }
    }

    private fun scheduleScoreUpdate() {
        val scoreUpdateRequest = PeriodicWorkRequestBuilder<ScoreUpdateWorker>(1, TimeUnit.HOURS)
            .setConstraints(
                Constraints.Builder()
                    .setRequiredNetworkType(NetworkType.CONNECTED)
                    .build()
            )
            .build()

        WorkManager.getInstance(this).enqueueUniquePeriodicWork(
            "HourlyScoreUpdate",
            ExistingPeriodicWorkPolicy.UPDATE,
            scoreUpdateRequest
        )
    }
}
