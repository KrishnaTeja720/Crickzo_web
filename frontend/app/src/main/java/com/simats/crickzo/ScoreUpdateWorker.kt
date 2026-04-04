package com.simats.crickzo

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters

class ScoreUpdateWorker(
    context: Context,
    workerParams: WorkerParameters
) : CoroutineWorker(context, workerParams) {

    override suspend fun doWork(): Result {
        return try {
            val sharedPrefs = applicationContext.getSharedPreferences("crickzo_prefs", Context.MODE_PRIVATE)
            val userId = sharedPrefs.getInt("user_id", -1)
            
            if (userId <= 0) {
                return Result.success()
            }
            
            val response = RetrofitClient.apiService.getLiveMatches(userId)
            if (response.isSuccessful) {
                val matches = response.body()
                if (!matches.isNullOrEmpty()) {
                    val match = matches[0] // Show the first live match
                    showNotification(
                        "Live Match: ${match.teamA} vs ${match.teamB}",
                        "Score: ${match.runs}/${match.wickets} (${match.overs} overs). CRR: ${match.crr}"
                    )
                }
            }
            Result.success()
        } catch (e: Exception) {
            // If failed, we still want to notify the user periodically
            showNotification(
                "Match Update",
                "Check out the latest scores and match predictions on Crickzo."
            )
            Result.retry()
        }
    }

    private fun showNotification(title: String, message: String) {
        val notificationManager = applicationContext.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        val channelId = "score_updates_channel"

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                channelId,
                "Score Updates",
                NotificationManager.IMPORTANCE_HIGH
            )
            notificationManager.createNotificationChannel(channel)
        }

        val intent = Intent(applicationContext, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        }
        val pendingIntent = PendingIntent.getActivity(
            applicationContext, 
            0, 
            intent, 
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
        )

        val notification = NotificationCompat.Builder(applicationContext, channelId)
            .setSmallIcon(android.R.drawable.ic_dialog_info) 
            .setContentTitle(title)
            .setContentText(message)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setContentIntent(pendingIntent)
            .setAutoCancel(true)
            .build()

        notificationManager.notify(1, notification)
    }
}
