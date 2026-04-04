package com.simats.crickzo

import com.google.gson.annotations.SerializedName

data class GenericResponse(
    @SerializedName("status") val status: String,
    @SerializedName("message") val message: String
)
