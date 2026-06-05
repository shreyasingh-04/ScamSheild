package com.scamdetector.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

// Brand Colors
val ShieldBlue = Color(0xFF0056D2)
val ScamRed = Color(0xFFD32F2F)
val SafeGreen = Color(0xFF388E3C)
val ScamOrange = Color(0xFFED8936)
val WarnYellow = Color(0xFFD69E2E)

@Composable
fun ScamShieldTheme(
    darkTheme: Boolean = false, 
    content: @Composable () -> Unit
) {
    MaterialTheme(
        colorScheme = lightColorScheme(
            primary = ShieldBlue,
            onPrimary = Color.White,
            background = Color.White,
            onBackground = Color.Black,
            surface = Color.White,
            onSurface = Color.Black,
            surfaceVariant = Color(0xFFF5F5F5)
        ),
        typography = ScamShieldTypography,
        content = content
    )
}
