package com.scamdetector.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.scamdetector.data.remote.TextAnalysisResponse
import com.scamdetector.data.remote.UrlAnalysisResponse
import com.scamdetector.data.remote.VoiceAnalysisResponse
import com.scamdetector.data.repository.ApiResult
import com.scamdetector.data.repository.ScamRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class AnalysisUiState(
    val isLoading: Boolean = false,
    val error: String? = null,
    val textResult: TextAnalysisResponse? = null,
    val urlResult: UrlAnalysisResponse? = null,
    val voiceResult: VoiceAnalysisResponse? = null,
    val analysisType: String? = null
)

@HiltViewModel
class AnalyzeViewModel @Inject constructor(
    private val repository: ScamRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(AnalysisUiState())
    val uiState: StateFlow<AnalysisUiState> = _uiState.asStateFlow()

    fun analyzeText(
        text: String,
        messageType: String = "sms",
        senderPhone: String? = null,
        isUnknownSender: Boolean = false,
        isInternational: Boolean = false
    ) {
        viewModelScope.launch {
            _uiState.value = AnalysisUiState(isLoading = true, analysisType = "text")
            when (val result = repository.analyzeText(text, messageType, senderPhone, isUnknownSender, isInternational)) {
                is ApiResult.Success -> _uiState.value = AnalysisUiState(textResult = result.data, analysisType = "text")
                is ApiResult.Error -> _uiState.value = AnalysisUiState(error = result.message, analysisType = "text")
                is ApiResult.Loading -> Unit
            }
        }
    }

    fun analyzeUrl(url: String) {
        viewModelScope.launch {
            _uiState.value = AnalysisUiState(isLoading = true, analysisType = "url")
            when (val result = repository.analyzeUrl(url)) {
                is ApiResult.Success -> _uiState.value = AnalysisUiState(urlResult = result.data, analysisType = "url")
                is ApiResult.Error -> _uiState.value = AnalysisUiState(error = result.message, analysisType = "url")
                is ApiResult.Loading -> Unit
            }
        }
    }

    fun analyzeEmail(subject: String, body: String, senderEmail: String? = null, hasAttachments: Boolean = false) {
        viewModelScope.launch {
            _uiState.value = AnalysisUiState(isLoading = true, analysisType = "email")
            when (val result = repository.analyzeEmail(subject, body, senderEmail, hasAttachments)) {
                is ApiResult.Success -> _uiState.value = AnalysisUiState(textResult = result.data, analysisType = "email")
                is ApiResult.Error -> _uiState.value = AnalysisUiState(error = result.message, analysisType = "email")
                is ApiResult.Loading -> Unit
            }
        }
    }

    fun analyzeVoice(transcript: String, callerId: String? = null) {
        viewModelScope.launch {
            _uiState.value = AnalysisUiState(isLoading = true, analysisType = "voice")
            when (val result = repository.analyzeVoice(transcript, callerId)) {
                is ApiResult.Success -> _uiState.value = AnalysisUiState(voiceResult = result.data, analysisType = "voice")
                is ApiResult.Error -> _uiState.value = AnalysisUiState(error = result.message, analysisType = "voice")
                is ApiResult.Loading -> Unit
            }
        }
    }

    fun clearResult() {
        _uiState.value = AnalysisUiState()
    }

    fun clearError() {
        _uiState.value = _uiState.value.copy(error = null)
    }
}
