package com.simats.crickzo

data class CreatedMatch(
    val id: String,
    val teamA: String,
    val teamB: String,
    val teamAPlayers: List<String> = emptyList(),
    val teamBPlayers: List<String> = emptyList(),
    val striker: String = "",
    val nonStriker: String = "",
    val bowler: String = "",
    val status: String,
    val location: String,
    val type: String = "T20"
)
