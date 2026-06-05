package com.scamdetector.ui.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import com.scamdetector.ui.screens.HomeScreen
import com.scamdetector.ui.screens.AnalyzeScreen
import com.scamdetector.ui.screens.DashboardScreen
import com.scamdetector.ui.screens.ChatbotScreen
import com.scamdetector.ui.screens.ReportScreen
import com.scamdetector.ui.screens.ResultScreen
import com.scamdetector.ui.screens.HistoryScreen

sealed class Screen(val route: String) {
    object Home : Screen("home")
    object Analyze : Screen("analyze")
    object Dashboard : Screen("dashboard")
    object Chatbot : Screen("chatbot")
    object Report : Screen("report")
    object Result : Screen("result/{analysisId}") {
        fun createRoute(analysisId: String) = "result/$analysisId"
    }
    object History : Screen("history")
}

@Composable
fun ScamShieldNavGraph(navController: NavHostController) {
    NavHost(
        navController = navController,
        startDestination = Screen.Home.route
    ) {
        composable(Screen.Home.route) {
            HomeScreen(navController = navController)
        }
        composable(Screen.Analyze.route) {
            AnalyzeScreen(navController = navController)
        }
        composable(Screen.Dashboard.route) {
            DashboardScreen(navController = navController)
        }
        composable(Screen.Chatbot.route) {
            ChatbotScreen(navController = navController)
        }
        composable(Screen.Report.route) {
            ReportScreen(navController = navController)
        }
        composable(Screen.History.route) {
            HistoryScreen(navController = navController)
        }
    }
}
