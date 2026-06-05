package com.scamdetector

import android.app.Application
import dagger.hilt.android.HiltAndroidApp

@HiltAndroidApp
class ScamShieldApplication : Application() {
    override fun onCreate() {
        super.onCreate()
    }
}
