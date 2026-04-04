package com.simats.crickzo

import android.content.Context
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Email
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Visibility
import androidx.compose.material.icons.filled.VisibilityOff
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.simats.crickzo.ui.theme.*
import kotlinx.coroutines.launch

@Composable
fun LoginScreen(
    onSignUpClick: () -> Unit,
    onForgotPasswordClick: () -> Unit,
    onLoginSuccess: (String, String, Int) -> Unit
) {
    val coroutineScope = rememberCoroutineScope()
    val apiService = RetrofitClient.apiService
    val snackbarHostState = remember { SnackbarHostState() }
    val context = LocalContext.current

    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var passwordVisible by remember { mutableStateOf(false) }
    var isLoading by remember { mutableStateOf(false) }

    fun handleLogin() {
        if (email.isBlank() || password.isBlank()) {
            coroutineScope.launch { snackbarHostState.showSnackbar("Please enter email and password") }
            return
        }

        isLoading = true
        coroutineScope.launch {
            try {
                val request = LoginRequest(email, password)
                val response = apiService.login(request)
                if (response.isSuccessful) {
                    val body = response.body()
                    if (body?.status == "success") {
                        val userId = body.userId ?: -1
                        val name = body.name ?: "User"
                        
                        val sharedPrefs = context.getSharedPreferences("crickzo_prefs", Context.MODE_PRIVATE)
                        sharedPrefs.edit()
                            .putInt("user_id", userId)
                            .putString("user_name", name)
                            .putString("user_email", email)
                            .apply()
                        
                        onLoginSuccess(name, email, userId)
                    } else {
                        snackbarHostState.showSnackbar(body?.message ?: "Login failed")
                    }
                } else {
                    snackbarHostState.showSnackbar("Error: ${response.message()}")
                }
            } catch (e: Exception) {
                snackbarHostState.showSnackbar("Network error: ${e.localizedMessage}")
            } finally {
                isLoading = false
            }
        }
    }

    Scaffold(
        snackbarHost = { SnackbarHost(snackbarHostState) }
    ) { padding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(brush = Brush.verticalGradient(colors = listOf(BgGradientStart, BgGradientEnd)))
                .padding(padding)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(horizontal = 24.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Spacer(modifier = Modifier.height(60.dp))

                Surface(modifier = Modifier.size(80.dp), shape = CircleShape, color = Color.White.copy(alpha = 0.2f)) {
                    Icon(imageVector = Icons.Default.Person, contentDescription = null, tint = Color.White, modifier = Modifier.padding(16.dp).fillMaxSize())
                }

                Spacer(modifier = Modifier.height(16.dp))
                Text(text = "User Login", color = Color.White, fontSize = 32.sp, fontWeight = FontWeight.Bold)
                Text(text = "Watch Live Matches & AI Predictions", color = Color.White.copy(alpha = 0.8f), fontSize = 16.sp)

                Spacer(modifier = Modifier.height(40.dp))

                Card(modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(24.dp), colors = CardDefaults.cardColors(containerColor = Color.White)) {
                    Column(modifier = Modifier.padding(24.dp).fillMaxWidth(), horizontalAlignment = Alignment.CenterHorizontally) {
                        Text(text = "Welcome Back", fontSize = 24.sp, fontWeight = FontWeight.Bold, color = Color.Black)
                        Text(text = "Sign in to watch live cricket matches", fontSize = 14.sp, color = GrayText, modifier = Modifier.padding(top = 8.dp))
                        Spacer(modifier = Modifier.height(32.dp))

                        Column(modifier = Modifier.fillMaxWidth()) {
                            Text(text = "Email Address", fontSize = 14.sp, fontWeight = FontWeight.Medium, color = Color.Black, modifier = Modifier.padding(bottom = 8.dp))
                            OutlinedTextField(
                                value = email, onValueChange = { email = it }, modifier = Modifier.fillMaxWidth(),
                                placeholder = { Text("Enter your email", color = Color.LightGray) },
                                leadingIcon = { Icon(Icons.Default.Email, null, tint = GrayText) },
                                shape = RoundedCornerShape(12.dp), singleLine = true,
                                colors = OutlinedTextFieldDefaults.colors(focusedBorderColor = PrimaryBlue, unfocusedBorderColor = Color(0xFFE5E7EB))
                            )
                        }

                        Spacer(modifier = Modifier.height(16.dp))

                        Column(modifier = Modifier.fillMaxWidth()) {
                            Text(text = "Password", fontSize = 14.sp, fontWeight = FontWeight.Medium, color = Color.Black, modifier = Modifier.padding(bottom = 8.dp))
                            OutlinedTextField(
                                value = password, onValueChange = { password = it }, modifier = Modifier.fillMaxWidth(),
                                placeholder = { Text("Enter your password", color = Color.LightGray) },
                                leadingIcon = { Icon(Icons.Default.Lock, null, tint = GrayText) },
                                trailingIcon = {
                                    IconButton(onClick = { passwordVisible = !passwordVisible }) {
                                        Icon(if (passwordVisible) Icons.Default.Visibility else Icons.Default.VisibilityOff, null, tint = GrayText)
                                    }
                                },
                                visualTransformation = if (passwordVisible) VisualTransformation.None else PasswordVisualTransformation(),
                                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
                                shape = RoundedCornerShape(12.dp), singleLine = true,
                                colors = OutlinedTextFieldDefaults.colors(focusedBorderColor = PrimaryBlue, unfocusedBorderColor = Color(0xFFE5E7EB))
                            )
                        }

                        Box(modifier = Modifier.fillMaxWidth().padding(top = 8.dp), contentAlignment = Alignment.CenterEnd) {
                            TextButton(onClick = onForgotPasswordClick) {
                                Text(text = "Forgot Password?", color = LinkBlue, fontSize = 14.sp)
                            }
                        }

                        Spacer(modifier = Modifier.height(16.dp))

                        Button(
                            onClick = { handleLogin() },
                            modifier = Modifier.fillMaxWidth().height(56.dp),
                            enabled = !isLoading,
                            shape = RoundedCornerShape(12.dp),
                            colors = ButtonDefaults.buttonColors(containerColor = PrimaryBlue)
                        ) {
                            if (isLoading) CircularProgressIndicator(color = Color.White, modifier = Modifier.size(24.dp))
                            else Text(text = "Sign In", fontSize = 18.sp, fontWeight = FontWeight.Bold)
                        }

                        Spacer(modifier = Modifier.height(24.dp))

                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text(text = "Don't have an account?", color = GrayText, fontSize = 14.sp)
                            TextButton(onClick = onSignUpClick) {
                                Text(text = "Sign Up", color = LinkBlue, fontSize = 14.sp, fontWeight = FontWeight.Bold)
                            }
                        }
                    }
                }

                Spacer(modifier = Modifier.weight(1f))
                Text(text = "By continuing, you agree to our Terms of Service\nand Privacy Policy", color = Color.White.copy(alpha = 0.7f), fontSize = 12.sp, textAlign = TextAlign.Center, modifier = Modifier.padding(bottom = 32.dp))
            }
        }
    }
}
