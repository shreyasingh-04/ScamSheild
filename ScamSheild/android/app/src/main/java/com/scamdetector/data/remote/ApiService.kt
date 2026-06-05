package com.scamdetector.data.remote

import com.google.gson.annotations.SerializedName
import retrofit2.Response
import retrofit2.http.*

// ─── Request Models ───────────────────────────────────────────────────────────

data class TextAnalysisRequest(
    val text: String,
    val sender: String? = null,
    @SerializedName("message_type") val messageType: String = "sms",
    @SerializedName("sender_phone") val senderPhone: String? = null,
    @SerializedName("is_unknown_sender") val isUnknownSender: Boolean = false,
    @SerializedName("is_international") val isInternational: Boolean = false,
    @SerializedName("message_frequency") val messageFrequency: Int = 1
)

data class UrlAnalysisRequest(
    val url: String,
    val context: String? = null
)

data class EmailAnalysisRequest(
    val subject: String,
    val body: String,
    @SerializedName("sender_email") val senderEmail: String? = null,
    @SerializedName("has_attachments") val hasAttachments: Boolean = false,
    @SerializedName("reply_to") val replyTo: String? = null
)

data class VoiceAnalysisRequest(
    val transcript: String,
    @SerializedName("caller_id") val callerId: String? = null,
    @SerializedName("call_duration") val callDuration: Int? = null
)

data class ChatRequest(
    val message: String,
    @SerializedName("conversation_history") val conversationHistory: List<ChatHistoryItem> = emptyList(),
    @SerializedName("user_id") val userId: String? = null
)

data class ChatHistoryItem(
    val role: String,
    val content: String
)

data class ScamReportRequest(
    @SerializedName("report_type") val reportType: String,
    @SerializedName("phone_number") val phoneNumber: String? = null,
    @SerializedName("email_address") val emailAddress: String? = null,
    val url: String? = null,
    @SerializedName("message_content") val messageContent: String? = null,
    @SerializedName("scam_type") val scamType: String? = null,
    val description: String,
    @SerializedName("reporter_location") val reporterLocation: String? = null,
    @SerializedName("financial_loss") val financialLoss: Double? = null
)

// ─── Response Models ──────────────────────────────────────────────────────────

data class TextAnalysisResponse(
    val type: String,
    val input: String,
    @SerializedName("message_type") val messageType: String?,
    @SerializedName("is_scam") val isScam: Boolean,
    val confidence: Double,
    @SerializedName("scam_type") val scamType: String?,
    @SerializedName("risk_score") val riskScore: Double,
    @SerializedName("risk_level") val riskLevel: String,
    @SerializedName("risk_breakdown") val riskBreakdown: Map<String, Double>?,
    val explanation: List<String>,
    @SerializedName("keyword_analysis") val keywordAnalysis: Map<String, List<String>>?,
    val recommendation: String,
    val timestamp: String
)

data class UrlAnalysisResponse(
    val type: String,
    val url: String,
    @SerializedName("is_safe") val isSafe: Boolean,
    val verdict: String,
    @SerializedName("safety_score") val safetyScore: Double,
    @SerializedName("risk_score") val riskScore: Double,
    @SerializedName("risk_level") val riskLevel: String,
    val confidence: Double,
    val flags: List<String>,
    val explanation: List<String>,
    @SerializedName("domain_info") val domainInfo: DomainInfo?,
    val recommendation: String,
    val timestamp: String
)

data class DomainInfo(
    val domain: String,
    @SerializedName("uses_https") val usesHttps: Boolean,
    @SerializedName("is_known_safe") val isKnownSafe: Boolean,
    @SerializedName("subdomain_count") val subdomainCount: Int,
    @SerializedName("spoofed_brand") val spoofedBrand: String?,
    @SerializedName("phishing_keywords_found") val phishingKeywordsFound: List<String>,
    @SerializedName("url_length") val urlLength: Int
)

data class VoiceAnalysisResponse(
    val type: String,
    @SerializedName("transcript_preview") val transcriptPreview: String,
    @SerializedName("caller_id") val callerId: String?,
    @SerializedName("is_scam") val isScam: Boolean,
    val confidence: Double,
    @SerializedName("scam_type") val scamType: String?,
    @SerializedName("risk_score") val riskScore: Double,
    @SerializedName("risk_level") val riskLevel: String,
    @SerializedName("flagged_phrases") val flaggedPhrases: List<String>,
    val explanation: List<String>,
    val recommendation: String,
    val timestamp: String
)

data class ChatResponse(
    val response: String,
    val source: String,
    @SerializedName("ml_context") val mlContext: String?,
    val timestamp: String
)

data class DashboardStats(
    @SerializedName("total_analyzed") val totalAnalyzed: Int,
    @SerializedName("scams_detected") val scamsDetected: Int,
    @SerializedName("safe_messages") val safeMessages: Int,
    @SerializedName("detection_rate") val detectionRate: Double,
    @SerializedName("crowd_reports") val crowdReports: Int,
    @SerializedName("scam_types") val scamTypes: Map<String, Int>,
    val timestamp: String
)

data class ReportResponse(
    val success: Boolean,
    @SerializedName("report_id") val reportId: String,
    val message: String,
    @SerializedName("next_steps") val nextSteps: List<String>
)

// ─── API Interface ────────────────────────────────────────────────────────────

interface ScamShieldApiService {

    // Analysis endpoints
    @POST("api/v1/analyze/text")
    suspend fun analyzeText(@Body request: TextAnalysisRequest): Response<TextAnalysisResponse>

    @POST("api/v1/analyze/url")
    suspend fun analyzeUrl(@Body request: UrlAnalysisRequest): Response<UrlAnalysisResponse>

    @POST("api/v1/analyze/email")
    suspend fun analyzeEmail(@Body request: EmailAnalysisRequest): Response<TextAnalysisResponse>

    @POST("api/v1/analyze/voice")
    suspend fun analyzeVoice(@Body request: VoiceAnalysisRequest): Response<VoiceAnalysisResponse>

    // Chatbot
    @POST("api/v1/chatbot/ask")
    suspend fun chatbotAsk(@Body request: ChatRequest): Response<ChatResponse>

    // Dashboard
    @GET("api/v1/dashboard/stats")
    suspend fun getDashboardStats(): Response<DashboardStats>

    @GET("api/v1/dashboard/trends")
    suspend fun getTrends(): Response<Map<String, Any>>

    // Reports
    @POST("api/v1/report/scam")
    suspend fun reportScam(@Body request: ScamReportRequest): Response<ReportResponse>

    @GET("api/v1/report/list")
    suspend fun getReports(@Query("limit") limit: Int = 50): Response<Map<String, Any>>

    // Health check
    @GET("health")
    suspend fun healthCheck(): Response<Map<String, String>>
}
