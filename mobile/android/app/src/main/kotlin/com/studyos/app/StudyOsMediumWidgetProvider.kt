package com.studyos.app

import android.appwidget.AppWidgetManager
import android.content.Context
import android.content.SharedPreferences
import android.widget.RemoteViews
import es.antonborri.home_widget.HomeWidgetLaunchIntent
import es.antonborri.home_widget.HomeWidgetProvider

/**
 * Medium home-screen widget — cache-fed via Flutter HomeWidgetService (Sprint-1.8).
 */
class StudyOsMediumWidgetProvider : HomeWidgetProvider() {

    override fun onUpdate(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetIds: IntArray,
        widgetData: SharedPreferences,
    ) {
        appWidgetIds.forEach { widgetId ->
            val views = RemoteViews(context.packageName, R.layout.studyos_medium_widget).apply {
                val pendingIntent =
                    HomeWidgetLaunchIntent.getActivity(context, MainActivity::class.java)
                setOnClickPendingIntent(R.id.widget_root, pendingIntent)

                val minutes = widgetData.getInt("today_study_minutes", 0)
                val goal = widgetData.getInt("daily_goal_minutes", 0)
                val progress = widgetData.getString("progress_label", "0%") ?: "0%"
                val plan = widgetData.getString("plan_title", "Plan yok") ?: "Plan yok"
                val pomodoro = widgetData.getString("pomodoro_label", "Pomodoro yok")
                    ?: "Pomodoro yok"
                val goalLabel = widgetData.getString("goal_label", "Hedef yok")
                    ?: "Hedef yok"

                setTextViewText(R.id.widget_title, "StudyOS")
                setTextViewText(
                    R.id.widget_study_line,
                    "Bugün: ${minutes} dk / Hedef: ${goal} dk ($progress)",
                )
                setTextViewText(R.id.widget_plan_line, plan)
                setTextViewText(R.id.widget_pomodoro_line, pomodoro)
                setTextViewText(R.id.widget_goal_line, goalLabel)
            }
            appWidgetManager.updateAppWidget(widgetId, views)
        }
    }
}
