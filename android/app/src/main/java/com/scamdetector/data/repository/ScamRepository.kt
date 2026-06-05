package com.scamdetector.data.repository

import com.scamdetector.data.remote.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import javax.inject.Inject
import javax.inject.Singleton

sealed class ApiResult<out T> {
    data class Success<T>(val data: T) : ApiResult<T>()
    data class Error(val message: String, val code: Int? = null) : ApiResult<Nothing>()
    object Loading : ApiResult<Nothing>()
}

@Singleton
class ScamRepository @Inject constructor(
    private val apiService: ScamShieldApiService
) {

    suspend fun analyzeText(
        text: String,
        messageType: String = "sms",
        senderPhone: String? = null,
        isUnknownSender: Boolean = false,
        isInternational: Boolean = false
    ): ApiResult<TextAnalysisResponse> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.analyzeText(
                TextAnalysisRequest(
                    text = text,
                    messageType = messageType,
                    senderPhone = senderPhone,
                    isUnknownSender = isUnknownSender,
                    isInternational = isInternational
                )
            )
            if (response.isSuccessful) {
                response.body()?.let { ApiResult.Success(it) }
                    ?: ApiResult.Error("Empty response from server")
            } else {
                ApiResult.Error("Analysis failed: ${response.code()}", response.code())
            }
        } catch (e: Exception) {
            ApiResult.Error("Connection error: ${e.localizedMessage ?: "Unknown error"}")
        }
    }

    suspend fun analyzeUrl(url: String): ApiResult<UrlAnalysisResponse> =
        withContext(Dispatchers.IO) {
            try {
                val response = apiService.analyzeUrl(UrlAnalysisRequest(url = url))
                if (response.isSuccessful) {
                    response.body()?.let { ApiResult.Success(it) }
                        ?: ApiResult.Error("Empty response")
                } else {
                    ApiResult.Error("URL analysis failed: ${response.code()}", response.code())
                }
            } catch (e: Exception) {
                ApiResult.Error("Connection error: ${e.localizedMessage ?: "Unknown error"}")
            }
        }

    suspend fun analyzeEmail(
        subject: String,
        body: String,
        senderEmail: String? = null,
        hasAttachments: Boolean = false
    ): ApiResult<TextAnalysisResponse> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.analyzeEmail(
                EmailAnalysisRequest(
                    subject = subject,
                    body = body,
                    senderEmail = senderEmail,
                    hasAttachments = hasAttachments
                )
            )
            if (response.isSuccessful) {
                response.body()?.let { ApiResult.Success(it) }
                    ?: ApiResult.Error("Empty response")
            } else {
                ApiResult.Error("Email analysis failed: ${response.code()}", response.code())
            }
        } catch (e: Exception) {
            ApiResult.Error("Connection error: ${e.localizedMessage ?: "Unknown error"}")
        }
    }

    suspend fun analyzeVoice(
        transcript: String,
        callerId: String? = null
    ): ApiResult<VoiceAnalysisResponse> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.analyzeVoice(
                VoiceAnalysisRequest(transcript = transcript, callerId = callerId)
            )
            if (response.isSuccessful) {
                response.body()?.let { ApiResult.Success(it) }
                    ?: ApiResult.Error("Empty response")
            } else {
                ApiResult.Error("Voice analysis failed: ${response.code()}", response.code())
            }
        } catch (e: Exception) {
            ApiResult.Error("Connection error: ${e.localizedMessage ?: "Unknown error"}")
        }
    }

    suspend fun chatbotAsk(
        message: String,
        history: List<ChatHistoryItem> = emptyList()
    ): ApiResult<ChatResponse> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.chatbotAsk(
                ChatRequest(message = message, conversationHistory = history)
            )
            if (response.isSuccessful) {
                response.body()?.let { ApiResult.Success(it) }
                    ?: ApiResult.Error("Empty response")
            } else {
                ApiResult.Error("Chatbot error: ${response.code()}", response.code())
            }
        } catch (e: Exception) {
            ApiResult.Error("Connection error: ${e.localizedMessage ?: "Unknown error"}")
        }
    }

    suspend fun getDashboardStats(): ApiResult<DashboardStats> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.getDashboardStats()
            if (response.isSuccessful) {
                response.body()?.let { ApiResult.Success(it) }
                    ?: ApiResult.Error("Empty response")
            } else {
                ApiResult.Error("Stats error: ${response.code()}", response.code())
            }
        } catch (e: Exception) {
            ApiResult.Error("Connection error: ${e.localizedMessage ?: "Unknown error"}")
        }
    }

    suspend fun reportScam(
        reportType: String,
        details: String,
        description: String,
        scamType: String? = null
    ): ApiResult<ReportResponse> = withContext(Dispatchers.IO) {
        try {
            val request = when (reportType) {
                "phone" -> ScamReportRequest(reportType = "phone", phoneNumber = details, description = description, scamType = scamType)
                "email" -> ScamReportRequest(reportType = "email", emailAddress = details, description = description, scamType = scamType)
                "url" -> ScamReportRequest(reportType = "url", url = details, description = description, scamType = scamType)
                else -> ScamReportRequest(reportType = "message", messageContent = details, description = description, scamType = scamType)
            }
            val response = apiService.reportScam(request)
            if (response.isSuccessful) {
                response.body()?.let { ApiResult.Success(it) }
                    ?: ApiResult.Error("Empty response")
            } else {
                ApiResult.Error("Report failed: ${response.code()}", response.code())
            }
        } catch (e: Exception) {
            ApiResult.Error("Connection error: ${e.localizedMessage ?: "Unknown error"}")
        }
    }
}
