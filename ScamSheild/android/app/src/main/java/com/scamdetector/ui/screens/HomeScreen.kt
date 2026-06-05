package com.scamdetector.ui.screens

import androidx.compose.animation.*
import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import com.scamdetector.ui.navigation.Screen
import com.scamdetector.ui.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(navController: NavController) {
    val scrollState = rememberScrollState()

    Scaffold(
        containerColor = Color.White,
        bottomBar = {
            BottomNavigationBar(navController = navController, currentRoute = Screen.Home.route)
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .verticalScroll(scrollState)
                .background(Color.White)
        ) {
            // Hero Header
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(ShieldBlue)
                    .padding(24.dp)
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Spacer(modifier = Modifier.height(16.dp))
                    
                    // Shield Icon
                    Box(
                        modifier = Modifier
                            .size(80.dp)
                            .background(Color.White.copy(alpha = 0.2f), shape = CircleShape),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = Icons.Default.Security,
                            contentDescription = "Shield",
                            tint = Color.White,
                            modifier = Modifier.size(44.dp)
                        )
                    }
                    
                    Spacer(modifier = Modifier.height(16.dp))
                    
                    Text(
                        text = "ScamShield AI",
                        style = MaterialTheme.typography.headlineMedium,
                        fontWeight = FontWeight.ExtraBold,
                        color = Color.White
                    )
                    
                    Text(
                        text = "Protect yourself from scams in real-time",
                        style = MaterialTheme.typography.bodyMedium,
                        color = Color.White.copy(alpha = 0.8f),
                        textAlign = TextAlign.Center,
                        modifier = Modifier.padding(top = 4.dp)
                    )
                    
                    Spacer(modifier = Modifier.height(20.dp))
                    
                    Button(
                        onClick = { navController.navigate(Screen.Analyze.route) },
                        modifier = Modifier.fillMaxWidth().height(52.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = Color.White, contentColor = ShieldBlue),
                        shape = RoundedCornerShape(12.dp)
                    ) {
                        Icon(imageVector = Icons.Default.Search, contentDescription = null, modifier = Modifier.size(20.dp))
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(text = "Quick Scan", fontSize = 16.sp, fontWeight = FontWeight.SemiBold)
                    }
                }
            }
            
            Column(
                modifier = Modifier.fillMaxWidth().padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                Text(text = "Protection Overview", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold, color = Color.Black)
                
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    StatCard(modifier = Modifier.weight(1f), icon = Icons.Default.Shield, value = "1,247", label = "Scams Blocked", color = SafeGreen)
                    StatCard(modifier = Modifier.weight(1f), icon = Icons.Default.Warning, value = "98.2%", label = "Accuracy", color = ShieldBlue)
                }
                
                Text(text = "Analyze Content", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold, color = Color.Black)
                AnalysisTypeGrid(navController)
                RecentAlertCard()
                ScamTipsCard()
                Spacer(modifier = Modifier.height(16.dp))
            }
        }
    }
}

@Composable
fun StatCard(modifier: Modifier = Modifier, icon: ImageVector, value: String, label: String, color: Color) {
    Card(
        modifier = modifier,
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = Color(0xFFF5F5F5))
    ) {
        Column(modifier = Modifier.padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
            Icon(imageVector = icon, contentDescription = null, tint = color, modifier = Modifier.size(28.dp))
            Spacer(modifier = Modifier.height(8.dp))
            Text(text = value, fontWeight = FontWeight.ExtraBold, fontSize = 20.sp, color = Color.Black)
            Text(text = label, style = MaterialTheme.typography.bodySmall, color = Color.Gray)
        }
    }
}

@Composable
fun AnalysisTypeGrid(navController: NavController) {
    val items = listOf(
        Triple(Icons.Default.Sms, "SMS / Text", ScamOrange),
        Triple(Icons.Default.Email, "Email", ShieldBlue),
        Triple(Icons.Default.Link, "URL / Link", SafeGreen),
        Triple(Icons.Default.Phone, "Voice Call", ScamRed),
    )

    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
        items.take(2).forEach { (icon, label, color) ->
            AnalysisTypeCard(modifier = Modifier.weight(1f), icon = icon, label = label, color = color, onClick = { navController.navigate(Screen.Analyze.route) })
        }
    }
    Spacer(modifier = Modifier.height(12.dp))
    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
        items.drop(2).forEach { (icon, label, color) ->
            AnalysisTypeCard(modifier = Modifier.weight(1f), icon = icon, label = label, color = color, onClick = { navController.navigate(Screen.Analyze.route) })
        }
    }
}

@Composable
fun AnalysisTypeCard(modifier: Modifier = Modifier, icon: ImageVector, label: String, color: Color, onClick: () -> Unit) {
    Card(
        onClick = onClick,
        modifier = modifier,
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = Color(0xFFF5F5F5))
    ) {
        Column(modifier = Modifier.fillMaxWidth().padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.Center) {
            Box(modifier = Modifier.size(48.dp).background(color.copy(alpha = 0.15f), shape = CircleShape), contentAlignment = Alignment.Center) {
                Icon(imageVector = icon, contentDescription = label, tint = color, modifier = Modifier.size(26.dp))
            }
            Spacer(modifier = Modifier.height(8.dp))
            Text(text = label, style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.Medium, textAlign = TextAlign.Center, color = Color.Black)
        }
    }
}

@Composable
fun RecentAlertCard() {
    Card(modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(12.dp), colors = CardDefaults.cardColors(containerColor = ScamRed.copy(alpha = 0.05f)), border = BorderStroke(1.dp, ScamRed.copy(alpha = 0.2f))) {
        Row(modifier = Modifier.padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
            Icon(imageVector = Icons.Default.Warning, contentDescription = null, tint = ScamRed, modifier = Modifier.size(24.dp))
            Spacer(modifier = Modifier.width(12.dp))
            Column {
                Text(text = "Recent Scam Alert", fontWeight = FontWeight.Bold, color = ScamRed)
                Text(text = "IRS phone scam surge detected in your area", style = MaterialTheme.typography.bodySmall, color = Color.Gray)
            }
        }
    }
}

@Composable
fun ScamTipsCard() {
    Card(modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(12.dp), colors = CardDefaults.cardColors(containerColor = Color(0xFFF5F5F5))) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(imageVector = Icons.Default.Lightbulb, contentDescription = null, tint = WarnYellow, modifier = Modifier.size(20.dp))
                Spacer(modifier = Modifier.width(8.dp))
                Text(text = "Safety Tip", fontWeight = FontWeight.Bold, color = Color.Black)
            }
            Spacer(modifier = Modifier.height(8.dp))
            Text(text = "Legitimate organizations NEVER ask for payment via gift cards. If anyone requests gift cards as payment, it's always a scam.", style = MaterialTheme.typography.bodyMedium, color = Color.DarkGray, lineHeight = 22.sp)
        }
    }
}

@Composable
fun BottomNavigationBar(navController: NavController, currentRoute: String) {
    NavigationBar(containerColor = Color.White) {
        val items = listOf(
            Triple(Screen.Home.route, Icons.Default.Home, "Home"),
            Triple(Screen.Analyze.route, Icons.Default.Search, "Analyze"),
            Triple(Screen.Dashboard.route, Icons.Default.Dashboard, "Dashboard"),
            Triple(Screen.Chatbot.route, Icons.Default.Chat, "Assistant"),
            Triple(Screen.Report.route, Icons.Default.Report, "Report"),
        )
        items.forEach { (route, icon, label) ->
            NavigationBarItem(
                icon = { Icon(imageVector = icon, contentDescription = label) },
                label = { Text(label, fontSize = 11.sp) },
                selected = currentRoute == route,
                onClick = {
                    if (currentRoute != route) {
                        navController.navigate(route) {
                            popUpTo(navController.graph.startDestinationId)
                            launchSingleTop = true
                        }
                    }
                }
            )
        }
    }
}
