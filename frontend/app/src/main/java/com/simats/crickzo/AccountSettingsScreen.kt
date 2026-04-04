package com.simats.crickzo

import android.widget.Toast
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.*
import androidx.compose.material.icons.automirrored.outlined.Logout
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import com.simats.crickzo.ui.theme.GrayText
import kotlinx.coroutines.launch

@Composable
fun AccountSettingsScreen(
    userId: Int,
    initialName: String,
    initialEmail: String,
    onBack: () -> Unit,
    onSave: (String, String) -> Unit,
    onLogout: () -> Unit,
    onForgotPasswordClick: () -> Unit = {}
) {
    var name by remember { mutableStateOf(initialName) }
    var email by remember { mutableStateOf(initialEmail) }
    
    // Original values from backend to compare against
    var originalName by remember { mutableStateOf(initialName) }
    var originalEmail by remember { mutableStateOf(initialEmail) }
    
    var showChangePasswordDialog by remember { mutableStateOf(false) }
    var showPrivacyPolicy by remember { mutableStateOf(false) }
    var showTermsOfService by remember { mutableStateOf(false) }
    var showLogoutConfirmation by remember { mutableStateOf(false) }
    var isLoading by remember { mutableStateOf(false) }
    
    val coroutineScope = rememberCoroutineScope()
    val context = LocalContext.current

    // Fetch latest data from backend on mount
    LaunchedEffect(userId) {
        if (userId <= 0) return@LaunchedEffect
        
        isLoading = true
        try {
            val response = RetrofitClient.apiService.getUserProfile(userId.toString())
            if (response.isSuccessful) {
                response.body()?.let { profile ->
                    profile.name?.let { 
                        name = it
                        originalName = it
                    }
                    profile.email?.let { 
                        email = it
                        originalEmail = it
                    }
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
        } finally {
            isLoading = false
        }
    }

    val hasChanges = name != originalName || email != originalEmail

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Black.copy(alpha = 0.5f))
            .clickable(onClick = onBack),
        contentAlignment = Alignment.Center
    ) {
        if (isLoading) {
            CircularProgressIndicator(color = Color.White)
        }

        Card(
            modifier = Modifier
                .fillMaxWidth(0.92f)
                .padding(vertical = 40.dp)
                .clickable(enabled = false) { },
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(containerColor = Color.White),
            elevation = CardDefaults.cardElevation(defaultElevation = 8.dp)
        ) {
            Column(
                modifier = Modifier
                    .padding(20.dp)
                    .verticalScroll(rememberScrollState())
            ) {
                // Header
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            imageVector = Icons.Outlined.Settings,
                            contentDescription = null,
                            tint = Color(0xFF1E40AF),
                            modifier = Modifier.size(24.dp)
                        )
                        Spacer(modifier = Modifier.width(12.dp))
                        Text(
                            text = "Account Settings",
                            fontSize = 20.sp,
                            fontWeight = FontWeight.Bold,
                            color = Color(0xFF1E293B)
                        )
                    }
                    IconButton(onClick = onBack) {
                        Icon(
                            imageVector = Icons.Default.Close,
                            contentDescription = "Close",
                            tint = Color(0xFF94A3B8)
                        )
                    }
                }
                
                Text(
                    text = "Manage your account information and preferences",
                    color = Color(0xFF64748B),
                    fontSize = 14.sp,
                    modifier = Modifier.padding(start = 36.dp)
                )

                Spacer(modifier = Modifier.height(24.dp))

                // Profile Information Section
                SettingsSectionHeader(icon = Icons.Outlined.Person, title = "Profile Information")
                Spacer(modifier = Modifier.height(16.dp))
                
                SettingsEditField(
                    label = "Name",
                    value = name,
                    onValueChange = { name = it }
                )
                
                Spacer(modifier = Modifier.height(12.dp))
                
                SettingsEditField(
                    label = "Email",
                    value = email,
                    onValueChange = { email = it }
                )

                Spacer(modifier = Modifier.height(24.dp))
                HorizontalDivider(color = Color(0xFFF1F5F9))
                Spacer(modifier = Modifier.height(24.dp))

                // Privacy & Security Section
                SettingsSectionHeader(icon = Icons.Outlined.Shield, title = "Privacy & Security")
                Spacer(modifier = Modifier.height(16.dp))
                SettingsActionRow(
                    icon = Icons.Outlined.Lock,
                    label = "Change Password",
                    onClick = onForgotPasswordClick
                )
                Spacer(modifier = Modifier.height(8.dp))
                SettingsActionRow(
                    icon = Icons.Outlined.PrivacyTip,
                    label = "Privacy Policy",
                    onClick = { showPrivacyPolicy = true }
                )
                Spacer(modifier = Modifier.height(8.dp))
                SettingsActionRow(
                    icon = Icons.Outlined.Article,
                    label = "Terms of Service",
                    onClick = { showTermsOfService = true }
                )

                Spacer(modifier = Modifier.height(24.dp))
                HorizontalDivider(color = Color(0xFFF1F5F9))
                Spacer(modifier = Modifier.height(24.dp))

                // Account Actions Section
                SettingsSectionHeader(icon = Icons.Outlined.ManageAccounts, title = "Account Actions")
                Spacer(modifier = Modifier.height(16.dp))
                SettingsActionRow(
                    icon = Icons.AutoMirrored.Outlined.Logout,
                    label = "Logout Session",
                    onClick = { showLogoutConfirmation = true }
                )

                Spacer(modifier = Modifier.height(32.dp))

                // Buttons
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    OutlinedButton(
                        onClick = onBack,
                        modifier = Modifier
                            .weight(1f)
                            .height(48.dp),
                        shape = RoundedCornerShape(8.dp),
                        border = BorderStroke(1.dp, Color(0xFFE2E8F0)),
                        colors = ButtonDefaults.outlinedButtonColors(contentColor = Color(0xFF475569))
                    ) {
                        Text("Cancel", fontWeight = FontWeight.SemiBold)
                    }
                    Button(
                        onClick = { 
                            if (!hasChanges) {
                                Toast.makeText(context, "No changes to save", Toast.LENGTH_SHORT).show()
                            } else {
                                onSave(name, email)
                                originalName = name
                                originalEmail = email
                                Toast.makeText(context, "Changes saved", Toast.LENGTH_SHORT).show()
                            }
                        },
                        enabled = hasChanges,
                        modifier = Modifier
                            .weight(1f)
                            .height(48.dp),
                        shape = RoundedCornerShape(8.dp),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = if (hasChanges) Color(0xFF1E40AF) else Color(0xFF94A3B8)
                        )
                    ) {
                        Text("Save Changes", fontWeight = FontWeight.SemiBold)
                    }
                }
            }
        }
    }

    if (showLogoutConfirmation) {
        AlertDialog(
            onDismissRequest = { showLogoutConfirmation = false },
            title = { Text("Logout") },
            text = { Text("Are you sure you want to log out from Crickzo?") },
            confirmButton = {
                Button(
                    onClick = {
                        showLogoutConfirmation = false
                        onLogout()
                    },
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFEF4444))
                ) {
                    Text("Logout", color = Color.White)
                }
            },
            dismissButton = {
                TextButton(onClick = { showLogoutConfirmation = false }) {
                    Text("Cancel")
                }
            }
        )
    }

    if (showChangePasswordDialog) {
        ChangePasswordDialog(
            userName = originalName,
            userEmail = originalEmail,
            onDismiss = { showChangePasswordDialog = false },
            onConfirm = { current, new, confirm ->
                if (new != confirm) {
                    Toast.makeText(context, "New passwords do not match", Toast.LENGTH_SHORT).show()
                } else if (current == new) {
                    Toast.makeText(context, "New password must be different from current password", Toast.LENGTH_SHORT).show()
                } else if (new.length < 6) {
                    Toast.makeText(context, "Password must be at least 6 characters", Toast.LENGTH_SHORT).show()
                } else {
                    coroutineScope.launch {
                        try {
                            val response = RetrofitClient.apiService.changePassword(
                                ChangePasswordRequest(originalEmail, current, new)
                            )
                            if (response.isSuccessful) {
                                Toast.makeText(context, "Password changed successfully", Toast.LENGTH_SHORT).show()
                                showChangePasswordDialog = false
                            } else {
                                Toast.makeText(context, "Invalid current password", Toast.LENGTH_SHORT).show()
                            }
                        } catch (e: Exception) {
                            Toast.makeText(context, "Connection error: ${e.message}", Toast.LENGTH_SHORT).show()
                        }
                    }
                }
            },
            onForgotPassword = {
                showChangePasswordDialog = false
                onForgotPasswordClick()
            }
        )
    }

    if (showPrivacyPolicy) {
        InfoDialog(
            title = "Privacy Policy",
            icon = Icons.Outlined.PrivacyTip,
            onDismiss = { showPrivacyPolicy = false },
            content = """
                Your privacy is important to us. It is Crickzo's policy to respect your privacy regarding any information we may collect from you across our website and other sites we own and operate.
                
                We only ask for personal information when we truly need it to provide a service to you. We collect it by fair and lawful means, with your knowledge and consent. We also let you know why we’re collecting it and how it will be used.
                
                We only retain collected information for as long as necessary to provide you with your requested service. What data we store, we’ll protect within commercially acceptable means to prevent loss and theft, as well as unauthorized access, disclosure, copying, use or modification.
                
                We don’t share any personally identifying information publicly or with third-parties, except when required to by law.
            """.trimIndent()
        )
    }

    if (showTermsOfService) {
        InfoDialog(
            title = "Terms of Service",
            icon = Icons.Outlined.Article,
            onDismiss = { showTermsOfService = false },
            content = """
                1. Terms
                By accessing the app at Crickzo, you are agreeing to be bound by these terms of service, all applicable laws and regulations, and agree that you are responsible for compliance with any applicable local laws. 
                
                2. Use License
                Permission is granted to temporarily download one copy of the materials (information or software) on Crickzo's app for personal, non-commercial transitory viewing only.
                
                3. Disclaimer
                The materials on Crickzo's app are provided on an 'as is' basis. Crickzo makes no warranties, expressed or implied, and hereby disclaims and negates all other warranties including, without limitation, implied warranties or conditions of merchantability, fitness for a particular purpose, or non-infringement of intellectual property or other violation of rights.
            """.trimIndent()
        )
    }
}

@Composable
fun InfoDialog(
    title: String,
    icon: ImageVector,
    content: String,
    onDismiss: () -> Unit
) {
    Dialog(
        onDismissRequest = onDismiss,
        properties = DialogProperties(usePlatformDefaultWidth = false)
    ) {
        Card(
            modifier = Modifier
                .fillMaxWidth(0.92f)
                .fillMaxHeight(0.7f)
                .padding(20.dp),
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(containerColor = Color.White),
            elevation = CardDefaults.cardElevation(defaultElevation = 8.dp)
        ) {
            Column(
                modifier = Modifier.padding(24.dp)
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(
                        modifier = Modifier.weight(1f),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            imageVector = icon,
                            contentDescription = null,
                            tint = Color(0xFF1E40AF),
                            modifier = Modifier.size(24.dp)
                        )
                        Spacer(modifier = Modifier.width(12.dp))
                        Text(
                            text = title,
                            fontSize = 20.sp,
                            fontWeight = FontWeight.Bold,
                            color = Color(0xFF1E293B),
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis
                        )
                    }
                    IconButton(onClick = onDismiss) {
                        Icon(Icons.Default.Close, contentDescription = "Close", tint = Color(0xFF94A3B8))
                    }
                }

                Spacer(modifier = Modifier.height(16.dp))

                Column(
                    modifier = Modifier
                        .weight(1f)
                        .verticalScroll(rememberScrollState())
                ) {
                    Text(
                        text = content,
                        color = Color(0xFF475569),
                        fontSize = 14.sp,
                        lineHeight = 20.sp
                    )
                }

                Spacer(modifier = Modifier.height(24.dp))

                Button(
                    onClick = onDismiss,
                    modifier = Modifier.fillMaxWidth().height(48.dp),
                    shape = RoundedCornerShape(8.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF1E40AF))
                ) {
                    Text("Close", fontWeight = FontWeight.SemiBold)
                }
            }
        }
    }
}

@Composable
fun ChangePasswordDialog(
    userName: String,
    userEmail: String,
    onDismiss: () -> Unit,
    onConfirm: (String, String, String) -> Unit,
    onForgotPassword: () -> Unit
) {
    var currentPassword by remember { mutableStateOf("") }
    var newPassword by remember { mutableStateOf("") }
    var confirmPassword by remember { mutableStateOf("") }
    
    var currentPasswordVisible by remember { mutableStateOf(false) }
    var newPasswordVisible by remember { mutableStateOf(false) }
    var confirmPasswordVisible by remember { mutableStateOf(false) }

    Dialog(
        onDismissRequest = onDismiss,
        properties = DialogProperties(usePlatformDefaultWidth = false)
    ) {
        Box(
            modifier = Modifier.fillMaxSize(),
            contentAlignment = Alignment.Center
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth(0.92f)
                    .verticalScroll(rememberScrollState())
                    .padding(vertical = 24.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                // Profile Header Overlay
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(160.dp)
                        .background(
                            brush = Brush.verticalGradient(
                                colors = listOf(Color(0xFF1E40AF), Color(0xFF2563EB))
                            ),
                            shape = RoundedCornerShape(topStart = 16.dp, topEnd = 16.dp)
                        ),
                    contentAlignment = Alignment.Center
                ) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Surface(
                            modifier = Modifier.size(60.dp),
                            shape = CircleShape,
                            color = Color.White.copy(alpha = 0.2f)
                        ) {
                            Box(contentAlignment = Alignment.Center) {
                                Icon(
                                    imageVector = Icons.Default.Person,
                                    contentDescription = null,
                                    tint = Color.White,
                                    modifier = Modifier.size(36.dp)
                                )
                            }
                        }
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            text = userName,
                            color = Color.White,
                            fontSize = 18.sp,
                            fontWeight = FontWeight.Bold
                        )
                        Text(
                            text = userEmail,
                            color = Color.White.copy(alpha = 0.8f),
                            fontSize = 13.sp
                        )
                    }
                }

                // Dialog Card (Lower part)
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(bottomStart = 16.dp, bottomEnd = 16.dp),
                    colors = CardDefaults.cardColors(containerColor = Color.White),
                    elevation = CardDefaults.cardElevation(defaultElevation = 8.dp)
                ) {
                    Column(
                        modifier = Modifier.padding(20.dp)
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Row(
                                modifier = Modifier.weight(1f),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Icon(
                                    imageVector = Icons.Outlined.Lock,
                                    contentDescription = null,
                                    tint = Color(0xFF1E40AF),
                                    modifier = Modifier.size(24.dp)
                                )
                                Spacer(modifier = Modifier.width(12.dp))
                                Text(
                                    text = "Change Password",
                                    fontSize = 18.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = Color(0xFF1E293B),
                                    maxLines = 1,
                                    overflow = TextOverflow.Ellipsis
                                )
                            }
                            IconButton(onClick = onDismiss) {
                                Icon(Icons.Default.Close, contentDescription = "Close", tint = Color(0xFF94A3B8))
                            }
                        }

                        Text(
                            text = "Enter your current password and choose a new one",
                            color = Color(0xFF64748B),
                            fontSize = 13.sp,
                            modifier = Modifier.padding(top = 4.dp)
                        )

                        Spacer(modifier = Modifier.height(20.dp))

                        SettingsPasswordField(
                            label = "Current Password",
                            value = currentPassword,
                            onValueChange = { currentPassword = it },
                            placeholder = "Enter current password",
                            isVisible = currentPasswordVisible,
                            onToggleVisibility = { currentPasswordVisible = !currentPasswordVisible }
                        )
                        
                        Box(
                            modifier = Modifier.fillMaxWidth(),
                            contentAlignment = Alignment.CenterEnd
                        ) {
                            TextButton(onClick = onForgotPassword) {
                                Text(
                                    text = "Forgot Password?",
                                    color = Color(0xFF2563EB),
                                    fontSize = 12.sp,
                                    fontWeight = FontWeight.Medium
                                )
                            }
                        }

                        Spacer(modifier = Modifier.height(8.dp))

                        SettingsPasswordField(
                            label = "New Password",
                            value = newPassword,
                            onValueChange = { newPassword = it },
                            placeholder = "Enter new password",
                            isVisible = newPasswordVisible,
                            onToggleVisibility = { newPasswordVisible = !newPasswordVisible }
                        )
                        
                        Text(
                            text = "Password must be at least 6 characters",
                            color = Color(0xFF94A3B8),
                            fontSize = 12.sp,
                            modifier = Modifier.padding(top = 4.dp, start = 2.dp)
                        )

                        Spacer(modifier = Modifier.height(16.dp))

                        SettingsPasswordField(
                            label = "Confirm New Password",
                            value = confirmPassword,
                            onValueChange = { confirmPassword = it },
                            placeholder = "Confirm new password",
                            isVisible = confirmPasswordVisible,
                            onToggleVisibility = { confirmPasswordVisible = !confirmPasswordVisible }
                        )

                        Spacer(modifier = Modifier.height(24.dp))

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(10.dp)
                        ) {
                            OutlinedButton(
                                onClick = onDismiss,
                                modifier = Modifier.weight(1f).height(48.dp),
                                shape = RoundedCornerShape(8.dp),
                                border = BorderStroke(1.dp, Color(0xFFE2E8F0)),
                                colors = ButtonDefaults.outlinedButtonColors(contentColor = Color(0xFF475569))
                            ) {
                                Text("Cancel", fontWeight = FontWeight.SemiBold, fontSize = 14.sp)
                            }
                            Button(
                                onClick = { onConfirm(currentPassword, newPassword, confirmPassword) },
                                modifier = Modifier.weight(1.6f).height(48.dp),
                                shape = RoundedCornerShape(8.dp),
                                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF1E40AF))
                            ) {
                                Text(
                                    text = "Change Password",
                                    fontWeight = FontWeight.SemiBold,
                                    fontSize = 13.sp,
                                    maxLines = 1,
                                    overflow = TextOverflow.Clip
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun SettingsPasswordField(
    label: String,
    value: String,
    onValueChange: (String) -> Unit,
    placeholder: String,
    isVisible: Boolean,
    onToggleVisibility: () -> Unit
) {
    Column {
        Text(
            text = label,
            fontSize = 14.sp,
            fontWeight = FontWeight.Bold,
            color = Color(0xFF1E293B)
        )
        Spacer(modifier = Modifier.height(8.dp))
        OutlinedTextField(
            value = value,
            onValueChange = onValueChange,
            modifier = Modifier.fillMaxWidth(),
            placeholder = { Text(placeholder, color = Color(0xFF94A3B8), fontSize = 14.sp) },
            shape = RoundedCornerShape(8.dp),
            trailingIcon = {
                val image = if (isVisible) Icons.Default.VisibilityOff else Icons.Default.Visibility
                IconButton(onClick = onToggleVisibility) {
                    Icon(imageVector = image, contentDescription = null, tint = Color(0xFF94A3B8))
                }
            },
            visualTransformation = if (isVisible) VisualTransformation.None else PasswordVisualTransformation(),
            colors = OutlinedTextFieldDefaults.colors(
                focusedBorderColor = Color(0xFF1E40AF),
                unfocusedBorderColor = Color(0xFFF1F5F9),
                focusedContainerColor = Color(0xFFF8FAFC),
                unfocusedContainerColor = Color(0xFFF8FAFC)
            ),
            textStyle = LocalTextStyle.current.copy(fontSize = 14.sp, color = Color(0xFF64748B)),
            singleLine = true
        )
    }
}

@Composable
fun SettingsEditField(label: String, value: String, onValueChange: (String) -> Unit) {
    Column(modifier = Modifier.padding(start = 30.dp)) {
        Text(
            text = label,
            fontSize = 13.sp,
            fontWeight = FontWeight.Bold,
            color = Color(0xFF1E293B)
        )
        Spacer(modifier = Modifier.height(8.dp))
        OutlinedTextField(
            value = value,
            onValueChange = onValueChange,
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(8.dp),
            colors = OutlinedTextFieldDefaults.colors(
                focusedBorderColor = Color(0xFF1E40AF),
                unfocusedBorderColor = Color(0xFFF1F5F9),
                focusedContainerColor = Color(0xFFF8FAFC),
                unfocusedContainerColor = Color(0xFFF8FAFC)
            ),
            textStyle = LocalTextStyle.current.copy(fontSize = 14.sp, color = Color(0xFF64748B)),
            singleLine = true
        )
    }
}

@Composable
fun SettingsSectionHeader(icon: ImageVector, title: String) {
    Row(verticalAlignment = Alignment.CenterVertically) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            tint = Color(0xFF1E40AF),
            modifier = Modifier.size(18.dp)
        )
        Spacer(modifier = Modifier.width(12.dp))
        Text(
            text = title,
            fontSize = 15.sp,
            fontWeight = FontWeight.Bold,
            color = Color(0xFF1E293B)
        )
    }
}

@Composable
fun SettingsActionRow(icon: ImageVector, label: String, onClick: () -> Unit = {}) {
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .padding(start = 30.dp),
        color = Color(0xFFF8FAFC),
        shape = RoundedCornerShape(8.dp),
        border = BorderStroke(1.dp, Color(0xFFF1F5F9))
    ) {
        Row(
            modifier = Modifier
                .clickable(onClick = onClick)
                .padding(12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = Color(0xFF64748B),
                modifier = Modifier.size(18.dp)
            )
            Spacer(modifier = Modifier.width(12.dp))
            Text(
                text = label,
                fontSize = 14.sp,
                fontWeight = FontWeight.Medium,
                color = Color(0xFF1E293B)
            )
        }
    }
}
