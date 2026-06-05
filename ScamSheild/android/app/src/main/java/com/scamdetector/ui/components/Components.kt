package com.scamdetector.ui.components

import androidx.compose.animation.core.*
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.scamdetector.ui.theme.*
import kotlin.math.cos
import kotlin.math.sin

@Composable
fun RiskScoreGauge(
    score: Float,
    modifier: Modifier = Modifier,
    animateOnLoad: Boolean = true
) {
    val animatedScore by animateFloatAsState(
        targetValue = if (animateOnLoad) score else score,
        animationSpec = tween(durationMillis = 1200, easing = EaseOutCubic),
        label = "risk_score_anim"
    )

    val gaugeColor = when {
        score >= 75 -> ScamRed
        score >= 50 -> ScamOrange
        score >= 30 -> WarnYellow
        else -> SafeGreen
    }

    val label = when {
        score >= 75 -> "CRITICAL"
        score >= 50 -> "HIGH RISK"
        score >= 30 -> "MEDIUM"
        else -> "SAFE"
    }

    Column(
        modifier = modifier,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Box(
            contentAlignment = Alignment.Center,
            modifier = Modifier.size(160.dp)
        ) {
            Canvas(modifier = Modifier.size(160.dp)) {
                val strokeWidth = 16.dp.toPx()
                val radius = (size.minDimension - strokeWidth) / 2
                val center = Offset(size.width / 2, size.height / 2)
                val startAngle = 150f
                val sweepAngle = 240f

                // Background arc
                drawArc(
                    color = Color.Gray.copy(alpha = 0.2f),
                    startAngle = startAngle,
                    sweepAngle = sweepAngle,
                    useCenter = false,
                    topLeft = Offset(center.x - radius, center.y - radius),
                    size = Size(radius * 2, radius * 2),
                    style = Stroke(width = strokeWidth, cap = StrokeCap.Round)
                )

                // Score arc
                drawArc(
                    color = gaugeColor,
                    startAngle = startAngle,
                    sweepAngle = sweepAngle * (animatedScore / 100f),
                    useCenter = false,
                    topLeft = Offset(center.x - radius, center.y - radius),
                    size = Size(radius * 2, radius * 2),
                    style = Stroke(width = strokeWidth, cap = StrokeCap.Round)
                )

                // Needle dot
                val needleAngle = Math.toRadians((startAngle + sweepAngle * (animatedScore / 100f)).toDouble())
                val needleX = center.x + (radius) * cos(needleAngle).toFloat()
                val needleY = center.y + (radius) * sin(needleAngle).toFloat()
                drawCircle(
                    color = gaugeColor,
                    radius = 8.dp.toPx(),
                    center = Offset(needleX, needleY)
                )
            }

            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Text(
                    text = "${animatedScore.toInt()}",
                    fontSize = 36.sp,
                    fontWeight = FontWeight.ExtraBold,
                    color = gaugeColor
                )
                Text(
                    text = "/ 100",
                    fontSize = 13.sp,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.5f)
                )
            }
        }

        Surface(
            shape = RoundedCornerShape(20.dp),
            color = gaugeColor.copy(alpha = 0.15f)
        ) {
            Text(
                text = label,
                modifier = Modifier.padding(horizontal = 16.dp, vertical = 6.dp),
                color = gaugeColor,
                fontWeight = FontWeight.Bold,
                fontSize = 13.sp,
                letterSpacing = 1.sp
            )
        }
    }
}

@Composable
fun ExplanationCard(
    explanations: List<String>,
    isScam: Boolean,
    modifier: Modifier = Modifier
) {
    val borderColor = if (isScam) ScamRed else SafeGreen
    val bgColor = if (isScam) ScamRed.copy(alpha = 0.06f) else SafeGreen.copy(alpha = 0.06f)
    val icon = if (isScam) Icons.Default.Warning else Icons.Default.CheckCircle
    val title = if (isScam) "Why this is flagged" else "Why this is safe"

    Card(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = bgColor),
        border = androidx.compose.foundation.BorderStroke(1.dp, borderColor.copy(alpha = 0.3f))
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(icon, contentDescription = null, tint = borderColor, modifier = Modifier.size(20.dp))
                Spacer(modifier = Modifier.width(8.dp))
                Text(title, fontWeight = FontWeight.Bold, color = borderColor)
            }

            Spacer(modifier = Modifier.height(12.dp))

            explanations.forEach { explanation ->
                Row(
                    modifier = Modifier.padding(vertical = 3.dp),
                    verticalAlignment = Alignment.Top
                ) {
                    Text(
                        text = if (isScam) "⚠" else "✓",
                        color = borderColor,
                        fontSize = 13.sp,
                        modifier = Modifier.width(20.dp)
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = explanation,
                        style = MaterialTheme.typography.bodySmall,
                        lineHeight = 18.sp,
                        modifier = Modifier.weight(1f)
                    )
                }
            }
        }
    }
}

@Composable
fun KeywordBadge(keyword: String, category: String) {
    val color = when (category.lowercase()) {
        "urgency" -> ScamOrange
        "financial" -> WarnYellow
        "threat" -> ScamRed
        "impersonation" -> Color(0xFF9B59B6)
        "personal_info" -> ShieldBlue
        else -> Color.Gray
    }

    Surface(
        shape = RoundedCornerShape(16.dp),
        color = color.copy(alpha = 0.15f)
    ) {
        Text(
            text = keyword,
            modifier = Modifier.padding(horizontal = 10.dp, vertical = 5.dp),
            color = color,
            fontSize = 12.sp,
            fontWeight = FontWeight.Medium
        )
    }
}

@Composable
fun ScamTypeBadge(scamType: String?) {
    if (scamType == null) return

    val (color, icon) = when {
        scamType.contains("Phishing", ignoreCase = true) -> Pair(ShieldBlue, "🎣")
        scamType.contains("Financial", ignoreCase = true) -> Pair(WarnYellow, "💰")
        scamType.contains("Romance", ignoreCase = true) -> Pair(Color(0xFFE91E63), "💔")
        scamType.contains("Government", ignoreCase = true) || scamType.contains("IRS", ignoreCase = true) -> Pair(ScamOrange, "🏛")
        scamType.contains("Job", ignoreCase = true) -> Pair(Color(0xFF9C27B0), "💼")
        scamType.contains("Lottery", ignoreCase = true) || scamType.contains("Prize", ignoreCase = true) -> Pair(WarnYellow, "🎰")
        scamType.contains("Tech", ignoreCase = true) -> Pair(ShieldBlue, "💻")
        scamType.contains("Voice", ignoreCase = true) -> Pair(ScamRed, "📞")
        else -> Pair(ScamRed, "⚠️")
    }

    Surface(
        shape = RoundedCornerShape(8.dp),
        color = color.copy(alpha = 0.12f),
        modifier = Modifier.padding(vertical = 4.dp)
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(icon, fontSize = 16.sp)
            Spacer(modifier = Modifier.width(6.dp))
            Text(scamType, color = color, fontWeight = FontWeight.SemiBold, fontSize = 14.sp)
        }
    }
}
