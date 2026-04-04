package com.simats.crickzo

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
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
fun SignUpScreen(onBackToLogin: () -> Unit, onSignUpSuccess: (String, String) -> Unit) {
    val coroutineScope = rememberCoroutineScope()
    val apiService = RetrofitClient.apiService
    val snackbarHostState = remember { SnackbarHostState() }

    var fullName by remember { mutableStateOf("") }
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var confirmPassword by remember { mutableStateOf("") }
    var passwordVisible by remember { mutableStateOf(false) }
    var confirmPasswordVisible by remember { mutableStateOf(false) }
    var isLoading by remember { mutableStateOf(false) }

    fun handleSignUp() {
        if (fullName.isBlank() || email.isBlank() || password.isBlank()) {
            coroutineScope.launch { snackbarHostState.showSnackbar("Please fill all fields") }
            return
        }
        if (password != confirmPassword) {
            coroutineScope.launch { snackbarHostState.showSnackbar("Passwords do not match") }
            return
        }
        if (password.length < 8) {
            coroutineScope.launch { snackbarHostState.showSnackbar("Password must be at least 8 characters") }
            return
        }

        isLoading = true
        coroutineScope.launch {
            try {
                val request = SignupRequest(fullName, email, password)
                val response = apiService.signup(request)
                if (response.isSuccessful && response.body()?.status == "success") {
                    onSignUpSuccess(email, fullName)
                } else {
                    snackbarHostState.showSnackbar(response.body()?.message ?: "Signup failed")
                }
            } catch (e: Exception) {
                snackbarHostState.showSnackbar("Connection error: ${e.localizedMessage}")
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
                    .verticalScroll(rememberScrollState())
                    .padding(horizontal = 24.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Spacer(modifier = Modifier.height(48.dp))

                Row(modifier = Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                    IconButton(onClick = onBackToLogin) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back", tint = Color.White)
                    }
                    Text(text = "Back to login", color = Color.White, fontSize = 16.sp)
                }

                Spacer(modifier = Modifier.height(16.dp))

                Surface(modifier = Modifier.size(80.dp), shape = CircleShape, color = Color.White.copy(alpha = 0.2f)) {
                    Icon(imageVector = Icons.Default.Person, contentDescription = null, tint = Color.White, modifier = Modifier.padding(16.dp).fillMaxSize())
                }

                Spacer(modifier = Modifier.height(16.dp))
                Text(text = "Create Account", color = Color.White, fontSize = 32.sp, fontWeight = FontWeight.Bold)
                Text(text = "Join CrickAI Community", color = Color.White.copy(alpha = 0.8f), fontSize = 16.sp)
                Spacer(modifier = Modifier.height(32.dp))

                Card(modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(24.dp), colors = CardDefaults.cardColors(containerColor = Color.White)) {
                    Column(modifier = Modifier.padding(24.dp).fillMaxWidth(), horizontalAlignment = Alignment.CenterHorizontally) {
                        Text(text = "Sign Up", fontSize = 24.sp, fontWeight = FontWeight.Bold, color = Color.Black)
                        Text(text = "Create your account to watch live matches", fontSize = 14.sp, color = GrayText, modifier = Modifier.padding(top = 8.dp))
                        Spacer(modifier = Modifier.height(24.dp))

                        Column(modifier = Modifier.fillMaxWidth()) {
                            Text(text = "Full Name", fontSize = 14.sp, fontWeight = FontWeight.Medium, color = Color.Black, modifier = Modifier.padding(bottom = 8.dp))
                            OutlinedTextField(
                                value = fullName, onValueChange = { fullName = it }, modifier = Modifier.fillMaxWidth(),
                                placeholder = { Text("Enter your full name", color = Color.LightGray) },
                                leadingIcon = { Icon(Icons.Default.Person, null, tint = GrayText) },
                                shape = RoundedCornerShape(12.dp), singleLine = true,
                                enabled = !isLoading,
                                colors = OutlinedTextFieldDefaults.colors(focusedBorderColor = PrimaryBlue, unfocusedBorderColor = Color(0xFFE5E7EB))
                            )
                        }

                        Spacer(modifier = Modifier.height(16.dp))

                        Column(modifier = Modifier.fillMaxWidth()) {
                            Text(text = "Email Address", fontSize = 14.sp, fontWeight = FontWeight.Medium, color = Color.Black, modifier = Modifier.padding(bottom = 8.dp))
                            OutlinedTextField(
                                value = email, onValueChange = { email = it }, modifier = Modifier.fillMaxWidth(),
                                placeholder = { Text("Enter your email", color = Color.LightGray) },
                                leadingIcon = { Icon(Icons.Default.Email, null, tint = GrayText) },
                                shape = RoundedCornerShape(12.dp), singleLine = true,
                                enabled = !isLoading,
                                colors = OutlinedTextFieldDefaults.colors(focusedBorderColor = PrimaryBlue, unfocusedBorderColor = Color(0xFFE5E7EB))
                            )
                        }

                        Spacer(modifier = Modifier.height(16.dp))

                        Column(modifier = Modifier.fillMaxWidth()) {
                            Text(text = "Password", fontSize = 14.sp, fontWeight = FontWeight.Medium, color = Color.Black, modifier = Modifier.padding(bottom = 8.dp))
                            OutlinedTextField(
                                value = password, onValueChange = { password = it }, modifier = Modifier.fillMaxWidth(),
                                placeholder = { Text("Create a password", color = Color.LightGray) },
                                leadingIcon = { Icon(Icons.Default.Lock, null, tint = GrayText) },
                                trailingIcon = {
                                    IconButton(onClick = { passwordVisible = !passwordVisible }) {
                                        Icon(if (passwordVisible) Icons.Default.Visibility else Icons.Default.VisibilityOff, null, tint = GrayText)
                                    }
                                },
                                visualTransformation = if (passwordVisible) VisualTransformation.None else PasswordVisualTransformation(),
                                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
                                shape = RoundedCornerShape(12.dp), singleLine = true,
                                enabled = !isLoading,
                                colors = OutlinedTextFieldDefaults.colors(focusedBorderColor = PrimaryBlue, unfocusedBorderColor = Color(0xFFE5E7EB))
                            )
                            Text(text = "Must be at least 8 characters", fontSize = 12.sp, color = GrayText, modifier = Modifier.padding(top = 4.dp))
                        }

                        Spacer(modifier = Modifier.height(16.dp))

                        Column(modifier = Modifier.fillMaxWidth()) {
                            Text(text = "Confirm Password", fontSize = 14.sp, fontWeight = FontWeight.Medium, color = Color.Black, modifier = Modifier.padding(bottom = 8.dp))
                            OutlinedTextField(
                                value = confirmPassword, onValueChange = { confirmPassword = it }, modifier = Modifier.fillMaxWidth(),
                                placeholder = { Text("Confirm your password", color = Color.LightGray) },
                                leadingIcon = { Icon(Icons.Default.Lock, null, tint = GrayText) },
                                trailingIcon = {
                                    IconButton(onClick = { confirmPasswordVisible = !confirmPasswordVisible }) {
                                        Icon(if (confirmPasswordVisible) Icons.Default.Visibility else Icons.Default.VisibilityOff, null, tint = GrayText)
                                    }
                                },
                                visualTransformation = if (confirmPasswordVisible) VisualTransformation.None else PasswordVisualTransformation(),
                                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
                                shape = RoundedCornerShape(12.dp), singleLine = true,
                                enabled = !isLoading,
                                colors = OutlinedTextFieldDefaults.colors(focusedBorderColor = PrimaryBlue, unfocusedBorderColor = Color(0xFFE5E7EB))
                            )
                        }

                        Spacer(modifier = Modifier.height(24.dp))

                        Button(
                            onClick = { handleSignUp() },
                            modifier = Modifier.fillMaxWidth().height(56.dp),
                            enabled = !isLoading,
                            shape = RoundedCornerShape(12.dp),
                            colors = ButtonDefaults.buttonColors(containerColor = PrimaryBlue)
                        ) {
                            if (isLoading) CircularProgressIndicator(color = Color.White, modifier = Modifier.size(24.dp))
                            else Text(text = "Create Account", fontSize = 18.sp, fontWeight = FontWeight.Bold)
                        }

                        Spacer(modifier = Modifier.height(24.dp))

                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text(text = "Already have an account?", color = GrayText, fontSize = 14.sp)
                            TextButton(onClick = onBackToLogin) {
                                Text(text = "Sign In", color = LinkBlue, fontSize = 14.sp, fontWeight = FontWeight.Bold)
                            }
                        }
                    }
                }
                Spacer(modifier = Modifier.height(32.dp))
                Text(text = "By signing up, you'll get access to live matches\nand AI predictions", color = Color.White.copy(alpha = 0.7f), fontSize = 12.sp, textAlign = TextAlign.Center, modifier = Modifier.padding(bottom = 32.dp))
            }
        }
    }
}
