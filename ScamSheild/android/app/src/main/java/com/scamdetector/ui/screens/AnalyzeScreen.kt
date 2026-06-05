package com.scamdetector.ui.screens

import androidx.compose.animation.*
import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.material3.TabRowDefaults.tabIndicatorOffset
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavController
import com.scamdetector.ui.navigation.Screen
import com.scamdetector.ui.theme.*
import com.scamdetector.ui.viewmodel.AnalyzeViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AnalyzeScreen(
    navController: NavController,
    viewModel: AnalyzeViewModel = hiltViewModel()
) {
    var selectedTab by remember { mutableStateOf(0) }
    var inputText by remember { mutableStateOf("") }
    val uiState by viewModel.uiState.collectAsState()

    val tabs = listOf(
        Pair(Icons.Default.Sms, "SMS/Text"),
        Pair(Icons.Default.Email, "Email"),
        Pair(Icons.Default.Link, "URL"),
        Pair(Icons.Default.Phone, "Voice"),
    )

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Analyze Content", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = { navController.popBackStack() }) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        },
        bottomBar = {
            BottomNavigationBar(navController = navController, currentRoute = Screen.Analyze.route)
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .verticalScroll(rememberScrollState())
        ) {
            ScrollableTabRow(
                selectedTabIndex = selectedTab,
                edgePadding = 16.dp,
                containerColor = MaterialTheme.colorScheme.surface,
                indicator = { tabPositions ->
                    TabRowDefaults.SecondaryIndicator(
                        modifier = Modifier.tabIndicatorOffset(tabPositions[selectedTab]),
                        color = ShieldBlue
                    )
                }
            ) {
                tabs.forEachIndexed { index, (icon, label) ->
                    Tab(
                        selected = selectedTab == index,
                        onClick = { 
                            selectedTab = index 
                            viewModel.clearResult()
                        },
                        icon = { Icon(icon, contentDescription = null, modifier = Modifier.size(18.dp)) },
                        text = { Text(label, fontSize = 13.sp) },
                        selectedContentColor = ShieldBlue,
                        unselectedContentColor = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                    )
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            Column(modifier = Modifier.padding(horizontal = 16.dp)) {
                when (selectedTab) {
                    0 -> TextInputSection(
                        value = inputText,
                        onValueChange = { inputText = it },
                        label = "Paste suspicious SMS or text message",
                        placeholder = "Forward or paste the suspicious message here...",
                        icon = Icons.Default.Sms
                    )
                    1 -> TextInputSection(
                        value = inputText,
                        onValueChange = { inputText = it },
                        label = "Paste email content",
                        placeholder = "Copy and paste the suspicious email body here...",
                        icon = Icons.Default.Email,
                        minLines = 6
                    )
                    2 -> TextInputSection(
                        value = inputText,
                        onValueChange = { inputText = it },
                        label = "Enter URL to check",
                        placeholder = "https://suspicious-website.com/...",
                        icon = Icons.Default.Link,
                        minLines = 1
                    )
                    3 -> TextInputSection(
                        value = inputText,
                        onValueChange = { inputText = it },
                        label = "Paste voice call transcript",
                        placeholder = "Type or paste what the caller said...",
                        icon = Icons.Default.Phone,
                        minLines = 5
                    )
                }

                Spacer(modifier = Modifier.height(16.dp))

                Button(
                    onClick = { 
                        when(selectedTab) {
                            0 -> viewModel.analyzeText(inputText)
                            1 -> viewModel.analyzeEmail(subject = "Unknown", body = inputText)
                            2 -> viewModel.analyzeUrl(inputText)
                            3 -> viewModel.analyzeVoice(inputText)
                        }
                    },
                    modifier = Modifier.fillMaxWidth().height(52.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = ShieldBlue),
                    shape = RoundedCornerShape(12.dp),
                    enabled = inputText.isNotBlank() && !uiState.isLoading
                ) {
                    if (uiState.isLoading) {
                        CircularProgressIndicator(modifier = Modifier.size(20.dp), color = Color.White, strokeWidth = 2.dp)
                    } else {
                        Icon(Icons.Default.Search, contentDescription = null, modifier = Modifier.size(20.dp))
                    }
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(text = if (uiState.isLoading) "Analyzing..." else "Analyze Now", fontSize = 16.sp, fontWeight = FontWeight.SemiBold)
                }

                if (uiState.error != null) {
                    Spacer(modifier = Modifier.height(16.dp))
                    Text(text = uiState.error!!, color = ScamRed, modifier = Modifier.padding(8.dp))
                }

                val analysisResult = when(selectedTab) {
                    0, 1 -> uiState.textResult?.isScam
                    2 -> uiState.urlResult?.let { !it.isSafe }
                    3 -> uiState.voiceResult?.isScam
                    else -> null
                }

                val riskScore = when(selectedTab) {
                    0, 1 -> uiState.textResult?.riskScore?.toInt()
                    2 -> uiState.urlResult?.riskScore?.toInt()
                    3 -> uiState.voiceResult?.riskScore?.toInt()
                    else -> null
                }

                if (analysisResult != null) {
                    Spacer(modifier = Modifier.height(20.dp))
                    ResultDisplay(isScam = analysisResult, score = riskScore ?: 0)
                    
                    Spacer(modifier = Modifier.height(16.dp))
                    
                    // Display explanation if available
                    val explanation = when(selectedTab) {
                        0, 1 -> uiState.textResult?.explanation
                        2 -> uiState.urlResult?.explanation
                        3 -> uiState.voiceResult?.explanation
                        else -> null
                    }
                    
                    if (!explanation.isNullOrEmpty()) {
                        Card(
                            modifier = Modifier.fillMaxWidth(),
                            colors = CardDefaults.cardColors(containerColor = Color.White),
                            border = BorderStroke(1.dp, Color.LightGray.copy(alpha = 0.5f))
                        ) {
                            Column(modifier = Modifier.padding(16.dp)) {
                                Text("Why this result?", fontWeight = FontWeight.Bold, color = ShieldBlue)
                                Spacer(modifier = Modifier.height(8.dp))
                                explanation.forEach { point ->
                                    Row(modifier = Modifier.padding(vertical = 4.dp)) {
                                        Text("•", color = ShieldBlue, fontWeight = FontWeight.Bold)
                                        Spacer(modifier = Modifier.width(8.dp))
                                        Text(point, fontSize = 14.sp, color = Color.DarkGray)
                                    }
                                }
                            }
                        }
                    }
                }
                
                Spacer(modifier = Modifier.height(24.dp))
            }
        }
    }
}

@Composable
fun TextInputSection(
    value: String,
    onValueChange: (String) -> Unit,
    label: String,
    placeholder: String,
    icon: ImageVector,
    minLines: Int = 4
) {
    Column {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Icon(icon, contentDescription = null, tint = ShieldBlue, modifier = Modifier.size(20.dp))
            Spacer(modifier = Modifier.width(8.dp))
            Text(label, style = MaterialTheme.typography.labelLarge, fontWeight = FontWeight.Medium)
        }
        Spacer(modifier = Modifier.height(8.dp))
        OutlinedTextField(
            value = value,
            onValueChange = onValueChange,
            modifier = Modifier.fillMaxWidth(),
            placeholder = { Text(placeholder, color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.4f)) },
            minLines = minLines,
            shape = RoundedCornerShape(12.dp),
            trailingIcon = if (value.isNotBlank()) {
                { IconButton(onClick = { onValueChange("") }) { Icon(Icons.Default.Clear, contentDescription = "Clear") } }
            } else null
        )
    }
}

@Composable
fun ResultDisplay(isScam: Boolean, score: Int) {
    val borderColor = if (isScam) ScamRed else SafeGreen
    val bgColor = if (isScam) ScamRed.copy(alpha = 0.08f) else SafeGreen.copy(alpha = 0.08f)

    Card(
        modifier = Modifier.fillMaxWidth().border(1.dp, borderColor.copy(alpha = 0.4f), RoundedCornerShape(12.dp)),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = bgColor)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(if (isScam) Icons.Default.Warning else Icons.Default.CheckCircle, contentDescription = null, tint = borderColor, modifier = Modifier.size(24.dp))
                Spacer(modifier = Modifier.width(8.dp))
                Text(text = if (isScam) "SCAM DETECTED" else "SAFE", color = borderColor, fontWeight = FontWeight.ExtraBold, fontSize = 18.sp)
            }
            Spacer(modifier = Modifier.height(12.dp))
            Text("Risk Score: $score/100", fontWeight = FontWeight.Bold, color = borderColor)
            
            if (isScam) {
                Spacer(modifier = Modifier.height(8.dp))
                Text("Warning: This content matches patterns commonly used in fraudulent activities. Do not share personal information or click links.", 
                    style = MaterialTheme.typography.bodySmall, color = Color.DarkGray)
            } else {
                Spacer(modifier = Modifier.height(8.dp))
                Text("This content appears to be safe based on our current analysis.", 
                    style = MaterialTheme.typography.bodySmall, color = Color.DarkGray)
            }
        }
    }
}
