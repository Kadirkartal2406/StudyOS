package com.studyos.app

import android.content.ContentValues
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Environment
import android.provider.MediaStore
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel
import java.io.File
import java.io.FileOutputStream

class MainActivity : FlutterActivity() {
    private val channelName = "studyos/pdf_storage"

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, channelName)
            .setMethodCallHandler { call, result ->
                when (call.method) {
                    "savePdfToDownloads" -> {
                        try {
                            val bytes = call.argument<ByteArray>("bytes")
                            val filename = call.argument<String>("filename")
                            val relativePath = call.argument<String>("relativePath")
                                ?: "Download/StudyOS/Günlük Denemeler"
                            if (bytes == null || filename.isNullOrBlank()) {
                                result.error("bad_args", "bytes and filename required", null)
                                return@setMethodCallHandler
                            }
                            val saved = savePdfToDownloads(bytes, filename, relativePath)
                            result.success(saved)
                        } catch (e: Exception) {
                            result.error("save_failed", e.message, null)
                        }
                    }
                    "openPdf" -> {
                        try {
                            val uriStr = call.argument<String>("uri")
                            val path = call.argument<String>("path")
                            openPdf(uriStr, path)
                            result.success(true)
                        } catch (e: Exception) {
                            result.error("open_failed", e.message, null)
                        }
                    }
                    else -> result.notImplemented()
                }
            }
    }

    private fun savePdfToDownloads(
        bytes: ByteArray,
        requestedName: String,
        relativePath: String,
    ): Map<String, String?> {
        val safeRelative = relativePath
            .trim('/')
            .replace('\\', '/')
            .let { if (it.startsWith("Download/")) it else "Download/$it" }

        val uniqueName = uniqueDisplayName(requestedName, safeRelative)

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            val resolver = applicationContext.contentResolver
            val collection = MediaStore.Downloads.getContentUri(MediaStore.VOLUME_EXTERNAL_PRIMARY)
            // MediaStore RELATIVE_PATH wants Environment.DIRECTORY_DOWNLOADS + subdirs
            val mediaRelative = safeRelative
                .removePrefix("Download/")
                .let { "${Environment.DIRECTORY_DOWNLOADS}/$it" }
                .trimEnd('/') + "/"

            val values = ContentValues().apply {
                put(MediaStore.MediaColumns.DISPLAY_NAME, uniqueName)
                put(MediaStore.MediaColumns.MIME_TYPE, "application/pdf")
                put(MediaStore.MediaColumns.RELATIVE_PATH, mediaRelative)
                put(MediaStore.MediaColumns.IS_PENDING, 1)
            }
            val uri = resolver.insert(collection, values)
                ?: throw IllegalStateException("MediaStore insert failed")
            resolver.openOutputStream(uri)?.use { it.write(bytes) }
                ?: throw IllegalStateException("Cannot open output stream")
            values.clear()
            values.put(MediaStore.MediaColumns.IS_PENDING, 0)
            resolver.update(uri, values, null, null)

            return mapOf(
                "filename" to uniqueName,
                "uri" to uri.toString(),
                "path" to null,
                "displayPath" to "$safeRelative/$uniqueName",
            )
        }

        @Suppress("DEPRECATION")
        val base = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS)
        val sub = safeRelative.removePrefix("Download/").trim('/')
        val dir = if (sub.isEmpty()) base else File(base, sub)
        if (!dir.exists() && !dir.mkdirs()) {
            throw IllegalStateException("Cannot create folder: ${dir.absolutePath}")
        }
        val outFile = File(dir, uniqueName)
        FileOutputStream(outFile).use { it.write(bytes) }
        // Notify media scanner
        val uri = Uri.fromFile(outFile)
        sendBroadcast(Intent(Intent.ACTION_MEDIA_SCANNER_SCAN_FILE, uri))
        return mapOf(
            "filename" to uniqueName,
            "uri" to uri.toString(),
            "path" to outFile.absolutePath,
            "displayPath" to "$safeRelative/$uniqueName",
        )
    }

    private fun uniqueDisplayName(requestedName: String, safeRelative: String): String {
        val base = requestedName.removeSuffix(".pdf").removeSuffix(".PDF")
        val ext = ".pdf"
        var candidate = "$base$ext"
        var n = 2
        while (existsInDownloads(candidate, safeRelative) && n < 100) {
            candidate = "${base}_$n$ext"
            n++
        }
        return candidate
    }

    private fun existsInDownloads(displayName: String, safeRelative: String): Boolean {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            val mediaRelative = safeRelative
                .removePrefix("Download/")
                .let { "${Environment.DIRECTORY_DOWNLOADS}/$it" }
                .trimEnd('/') + "/"
            val projection = arrayOf(MediaStore.MediaColumns._ID)
            val selection =
                "${MediaStore.MediaColumns.DISPLAY_NAME}=? AND ${MediaStore.MediaColumns.RELATIVE_PATH}=?"
            applicationContext.contentResolver.query(
                MediaStore.Downloads.getContentUri(MediaStore.VOLUME_EXTERNAL_PRIMARY),
                projection,
                selection,
                arrayOf(displayName, mediaRelative),
                null,
            )?.use { cursor ->
                return cursor.moveToFirst()
            }
            return false
        }
        @Suppress("DEPRECATION")
        val base = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS)
        val sub = safeRelative.removePrefix("Download/").trim('/')
        val dir = if (sub.isEmpty()) base else File(base, sub)
        return File(dir, displayName).exists()
    }

    private fun openPdf(uriStr: String?, path: String?) {
        val uri: Uri = when {
            !uriStr.isNullOrBlank() -> Uri.parse(uriStr)
            !path.isNullOrBlank() -> {
                val file = File(path)
                // Prefer FileProvider-less content for legacy file:// only as last resort
                Uri.fromFile(file)
            }
            else -> throw IllegalArgumentException("uri or path required")
        }
        val intent = Intent(Intent.ACTION_VIEW).apply {
            setDataAndType(uri, "application/pdf")
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        }
        startActivity(Intent.createChooser(intent, "PDF'yi aç"))
    }
}
