package com.scamdetector.ui.screens

import android.util.Log
import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import com.scamdetector.ui.navigation.Screen
import com.scamdetector.ui.theme.*
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONArray
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

data class ChatMessage(val content: String, val isUser: Boolean)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ChatbotScreen(navController: NavController) {
    val messages = remember { mutableStateListOf(ChatMessage("Hello! I'm ScamShield AI. How can I help you stay safe today?", false)) }
    var inputText by remember { mutableStateOf("") }
    val coroutineScope = rememberCoroutineScope()
    val listState = rememberLazyListState()
    var isTyping by remember { mutableStateOf(false) }

    Scaffold(
        containerColor = Color.White,
        topBar = {
            TopAppBar(
                title = { 
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Box(
                            modifier = Modifier.size(8.dp).background(SafeGreen, CircleShape)
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("AI Assistant", fontWeight = FontWeight.Bold, color = Color.Black)
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = Color.White)
            )
        },
        bottomBar = { BottomNavigationBar(navController = navController, currentRoute = Screen.Chatbot.route) }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .background(Color(0xFFF8F9FA))
        ) {
            // Message List
            LazyColumn(
                state = listState,
                modifier = Modifier
                    .weight(1f)
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
                contentPadding = PaddingValues(vertical = 16.dp)
            ) {
                items(messages) { message ->
                    ChatBubble(message)
                }
                if (isTyping) {
                    item {
                        Text("ScamShield is thinking...", style = MaterialTheme.typography.bodySmall, color = Color.Gray, modifier = Modifier.padding(start = 8.dp))
                    }
                }
            }

            // Input Area
            Surface(
                tonalElevation = 2.dp,
                color = Color.White,
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(
                    modifier = Modifier
                        .padding(12.dp)
                        .navigationBarsPadding()
                        .imePadding(),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    TextField(
                        value = inputText,
                        onValueChange = { inputText = it },
                        placeholder = { Text("Ask me about a suspicious link...") },
                        modifier = Modifier.weight(1f),
                        colors = TextFieldDefaults.colors(
                            focusedContainerColor = Color(0xFFF1F3F4),
                            unfocusedContainerColor = Color(0xFFF1F3F4),
                            focusedIndicatorColor = Color.Transparent,
                            unfocusedIndicatorColor = Color.Transparent
                        ),
                        shape = RoundedCornerShape(24.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    IconButton(
                        onClick = {
                            if (inputText.isNotBlank()) {
                                val userMsg = inputText
                                messages.add(ChatMessage(userMsg, true))
                                inputText = ""
                                isTyping = true
                                
                                coroutineScope.launch {
                                    listState.animateScrollToItem(messages.size - 1)
                                    val response = sendMessageToBackend(userMsg, messages)
                                    isTyping = false
                                    messages.add(ChatMessage(response, false))
                                    listState.animateScrollToItem(messages.size - 1)
                                }
                            }
                        },
                        enabled = inputText.isNotBlank() && !isTyping,
                        colors = IconButtonDefaults.iconButtonColors(
                            containerColor = ShieldBlue,
                            contentColor = Color.White,
                            disabledContainerColor = Color.LightGray
                        )
                    ) {
                        Icon(Icons.Default.Send, contentDescription = "Send")
                    }
                }
            }
        }
    }
}

@Composable
fun ChatBubble(message: ChatMessage) {
    val alignment = if (message.isUser) Alignment.End else Alignment.Start
    val containerColor = if (message.isUser) ShieldBlue else Color.White
    val contentColor = if (message.isUser) Color.White else Color.Black
    val shape = if (message.isUser) {
        RoundedCornerShape(16.dp, 16.dp, 2.dp, 16.dp)
    } else {
        RoundedCornerShape(16.dp, 16.dp, 16.dp, 2.dp)
    }

    Column(modifier = Modifier.fillMaxWidth(), horizontalAlignment = alignment) {
        Surface(
            color = containerColor,
            shape = shape,
            shadowElevation = 1.dp
        ) {
            Text(
                text = message.content,
                modifier = Modifier.padding(horizontal = 16.dp, vertical = 10.dp),
                color = contentColor,
                fontSize = 15.sp
            )
        }
        Text(
            text = if (message.isUser) "You" else "ScamShield AI",
            style = MaterialTheme.typography.bodySmall,
            color = Color.Gray,
            modifier = Modifier.padding(top = 4.dp, start = 4.dp, end = 4.dp)
        )
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DashboardScreen(navController: NavController) {
    Scaffold(
        containerColor = Color.White,
        topBar = {
            TopAppBar(
                title = { Text("Analytics Dashboard", fontWeight = FontWeight.Bold, color = Color.Black) },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = Color.White)
            )
        },
        bottomBar = { BottomNavigationBar(navController = navController, currentRoute = Screen.Dashboard.route) }
    ) { padding ->
        Box(modifier = Modifier.fillMaxSize().padding(padding).background(Color.White), contentAlignment = Alignment.Center) {
            Text("Dashboard features coming soon...", color = Color.Black)
        }
    }
}

/**
 * Connects to the FastAPI backend chatbot endpoint
 */
suspend fun sendMessageToBackend(userMessage: String, history: List<ChatMessage>): String {
    return withContext(Dispatchers.IO) {
        try {
            val url = URL("http://10.0.2.2:8000/api/v1/chatbot/ask")
            val conn = url.openConnection() as HttpURLConnection
            conn.requestMethod = "POST"
            conn.setRequestProperty("Content-Type", "application/json")
            conn.doOutput = true

            // Create history JSON
            val historyArray = JSONArray()
            history.takeLast(5).forEach { 
                val msgObj = JSONObject()
                msgObj.put("role", if (it.isUser) "user" else "assistant")
                msgObj.put("content", it.content)
                historyArray.put(msgObj)
            }

            val jsonRequest = JSONObject().apply {
                put("message", userMessage)
                put("conversation_history", historyArray)
            }

            conn.outputStream.use { os ->
                os.write(jsonRequest.toString().toByteArray())
            }

            if (conn.responseCode == 200) {
                val response = conn.inputStream.bufferedReader().use { it.readText() }
                val jsonResponse = JSONObject(response)
                jsonResponse.getString("response")
            } else {
                Log.e("Chatbot", "Error: ${conn.responseCode} - ${conn.responseMessage}")
                "Sorry, I'm having trouble connecting to my brain right now. Please try again later."
            }
        } catch (e: Exception) {
            Log.e("Chatbot", "Connection failed", e)
            "Connection error: Please make sure the backend is running at http://localhost:8000"
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ReportScreen(navController: NavController) {
    Scaffold(
        containerColor = Color.White,
        topBar = {
            TopAppBar(
                title = { Text("Report a Scam", fontWeight = FontWeight.Bold, color = Color.Black) },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = Color.White)
            )
        },
        bottomBar = { BottomNavigationBar(navController = navController, currentRoute = Screen.Report.route) }
    ) { padding ->
        Box(modifier = Modifier.fillMaxSize().padding(padding).background(Color.White), contentAlignment = Alignment.Center) {
            Text("Reporting system coming soon...", color = Color.Black)
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HistoryScreen(navController: NavController) {
    Scaffold(
        containerColor = Color.White,
        topBar = {
            TopAppBar(
                title = { Text("Scan History", fontWeight = FontWeight.Bold, color = Color.Black) },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = Color.White)
            )
        },
        bottomBar = { BottomNavigationBar(navController = navController, currentRoute = Screen.History.route) }
    ) { padding ->
        Box(modifier = Modifier.fillMaxSize().padding(padding).background(Color.White), contentAlignment = Alignment.Center) {
            Text("History details coming soon...", color = Color.Black)
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ResultScreen(navController: NavController) {
    Scaffold(
        containerColor = Color.White,
        topBar = {
            TopAppBar(
                title = { Text("Analysis Result", fontWeight = FontWeight.Bold, color = Color.Black) },
                navigationIcon = {
                    IconButton(onClick = { navController.popBackStack() }) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back", tint = Color.Black)
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = Color.White)
            )
        }
    ) { padding ->
        Box(modifier = Modifier.fillMaxSize().padding(padding).background(Color.White), contentAlignment = Alignment.Center) {
            Text("Analysis details will appear here", color = Color.Black)
        }
    }
}
