package com.simats.crickzo

import com.google.gson.annotations.SerializedName

// Auth Models
data class LoginRequest(
    @SerializedName("email") val email: String,
    @SerializedName("password") val password: String
)

data class LoginResponse(
    @SerializedName("status") val status: String,
    @SerializedName("user_id") val userId: Int?,
    @SerializedName("name") val name: String?,
    @SerializedName("message") val message: String?
)

data class SignupRequest(
    @SerializedName("name") val name: String,
    @SerializedName("email") val email: String,
    @SerializedName("password") val password: String
)

data class SignupResponse(
    @SerializedName("status") val status: String,
    @SerializedName("message") val message: String
)

data class UserProfileResponse(
    @SerializedName("name") val name: String?,
    @SerializedName("email") val email: String?,
    @SerializedName("bio") val bio: String? = null,
    @SerializedName("matches_played") val matchesPlayed: Int = 0
)

data class ForgotPasswordRequest(
    @SerializedName("email") val email: String
)

data class ForgotPasswordResponse(
    @SerializedName("status") val status: String,
    @SerializedName("message") val message: String
)

data class VerifyOtpRequest(
    @SerializedName("email") val email: String,
    @SerializedName("otp") val otp: String
)

data class VerifyOtpResponse(
    @SerializedName("status") val status: String,
    @SerializedName("message") val message: String
)

data class ResetPasswordRequest(
    @SerializedName("email") val email: String,
    @SerializedName("otp") val otp: String,
    @SerializedName("new_password") val newPassword: String
)

data class ResetPasswordResponse(
    @SerializedName("status") val status: String,
    @SerializedName("message") val message: String
)

data class ResendOtpRequest(
    @SerializedName("email") val email: String
)

data class ResendOtpResponse(
    @SerializedName("status") val status: String,
    @SerializedName("message") val message: String
)

data class ChangePasswordRequest(
    @SerializedName("email") val email: String,
    @SerializedName("current_password") val currentPassword: String,
    @SerializedName("new_password") val newPassword: String
)

// Match Models
data class CreateMatchRequest(
    @SerializedName("user_id") val user_id: Int,
    @SerializedName("team_a") val team_a: String,
    @SerializedName("team_b") val team_b: String,
    @SerializedName("format") val format: String,
    @SerializedName("venue") val venue: String,
    @SerializedName("toss") val toss: String,
    @SerializedName("pitch") val pitch: String,
    @SerializedName("weather") val weather: String
)

data class CreateMatchResponse(
    @SerializedName("status") val status: String,
    @SerializedName("match_id") val matchId: Int,
    @SerializedName("message") val message: String
)

data class MatchDetailsResponse(
    @SerializedName("team_a") val teamA: String?,
    @SerializedName("team_b") val teamB: String?,
    @SerializedName("venue") val venue: String?,
    @SerializedName("format") val format: String?,
    @SerializedName("runs") val runs: Int = 0,
    @SerializedName("wickets") val wickets: Int = 0,
    @SerializedName("overs") val overs: Float = 0f,
    @SerializedName("crr") val crr: Float = 0f,
    @SerializedName("striker") val striker: String? = null,
    @SerializedName("non_striker") val nonStriker: String? = null,
    @SerializedName("bowler") val bowler: String? = null
)

data class Player(
    @SerializedName("player_name") val playerName: String,
    @SerializedName("team_name") val teamName: String,
    @SerializedName("role") val role: String? = null
)

data class MatchSetupRequest(
    @SerializedName("match_id") val matchId: Int,
    @SerializedName("team_a_players") val teamAPlayers: List<String>,
    @SerializedName("team_b_players") val teamBPlayers: List<String>
)

data class StartMatchRequest(
    @SerializedName("match_id") val matchId: Int,
    @SerializedName("striker") val striker: String,
    @SerializedName("non_striker") val nonStriker: String,
    @SerializedName("bowler") val bowler: String
)

data class BallInputRequest(
    @SerializedName("match_id") val matchId: Int,
    @SerializedName("innings") val innings: Int,
    @SerializedName("batsman") val batsman: String,
    @SerializedName("bowler") val bowler: String,
    @SerializedName("runs") val runs: Int,              // runs from bat
    @SerializedName("extras_type") val extrasType: String,   // NONE | WIDE | NOBALL | PENALTY
    @SerializedName("extras") val extras: Int,               // extra runs added
    @SerializedName("wicket") val wicket: Int,
    @SerializedName("wicket_type") val wicketType: String? = null  // RUNOUT | BOWLED | etc
)

data class ScoreResponse(
    @SerializedName("runs") val runs: Int = 0,
    @SerializedName("wickets") val wickets: Int = 0,
    @SerializedName("overs") val overs: Float = 0f,
    @SerializedName("crr") val crr: Float = 0f,
    @SerializedName("striker") val striker: String? = null,
    @SerializedName("non_striker") val nonStriker: String? = null,
    @SerializedName("bowler") val bowler: String? = null
)

data class BatsmanStat(
    @SerializedName("batsman") val batsman: String?,
    @SerializedName("runs") val runs: Int = 0,
    @SerializedName("balls") val balls: Int = 0,
    @SerializedName("fours") val fours: Int = 0,
    @SerializedName("sixes") val sixes: Int = 0,
    @SerializedName("strike_rate") val strikeRate: Double = 0.0
)

data class BowlerStat(
    @SerializedName("bowler") val bowler: String?,
    @SerializedName("overs") val overs: String?,
    @SerializedName("runs") val runs: Int = 0,
    @SerializedName("wickets") val wickets: Int = 0,
    @SerializedName("economy") val economy: Double = 0.0
)

typealias BowlerResponse = BowlerStat

data class PartnershipResponse(
    @SerializedName("runs") val runs: Int = 0,
    @SerializedName("balls") val balls: Int = 0
)

data class LiveMatchData(
    @SerializedName("match_id") val matchId: Int,
    @SerializedName("team_a") val teamA: String?,
    @SerializedName("team_b") val teamB: String?,
    @SerializedName("venue") val venue: String?,
    @SerializedName("runs") val runs: Int = 0,
    @SerializedName("wickets") val wickets: Int = 0,
    @SerializedName("overs") val overs: Float = 0f,
    @SerializedName("crr") val crr: Float = 0f,
    @SerializedName("striker") val striker: String? = null,
    @SerializedName("non_striker") val nonStriker: String? = null,
    @SerializedName("striker_runs") val strikerRuns: Int = 0,
    @SerializedName("non_striker_runs") val nonStrikerRuns: Int = 0
)

data class CompletedMatchInfo(
    @SerializedName("match_id") val matchId: Int,
    @SerializedName("team_a") val teamA: String?,
    @SerializedName("team_b") val teamB: String?,
    @SerializedName("venue") val venue: String?,
    @SerializedName("team_a_runs") val teamARuns: Int = 0,
    @SerializedName("team_a_wickets") val teamAWickets: Int = 0,
    @SerializedName("team_a_overs") val teamAOvers: Float = 0f,
    @SerializedName("team_b_runs") val teamBRuns: Int = 0,
    @SerializedName("team_b_wickets") val teamBWickets: Int = 0,
    @SerializedName("team_b_overs") val teamBOvers: Float = 0f,
    @SerializedName("winner") val winner: String?,
    @SerializedName("result") val result: String?
)

data class MatchPredictions(
    @SerializedName("winner_prediction") val winnerPrediction: WinnerPrediction?,
    @SerializedName("projected_score") val projectedScore: ProjectedScore?,
    @SerializedName("phase_analysis") val phaseAnalysis: PhaseAnalysis?,
    @SerializedName("next_over") val nextOver: PredictionDetail?,
    @SerializedName("next_5_overs") val next5Overs: PredictionDetail?,
    @SerializedName("wicket_probability") val wicketProbability: Int = 0,
    @SerializedName("partnership_forecast") val partnershipForecast: PartnershipForecast?,
    @SerializedName("batsman_forecast") val batsmanForecast: List<BatsmanForecast>? = null,
    @SerializedName("death_overs_score") val deathOversScore: PredictionDetail?
)

data class WinnerPrediction(
    @SerializedName("teamA") val teamA: Int = 50,
    @SerializedName("teamB") val teamB: Int = 50
)

data class ProjectedScore(
    @SerializedName("range") val range: String? = "150-170",
    @SerializedName("confidence") val confidence: Int = 0
)

data class PhaseAnalysis(
    @SerializedName("phase") val phase: String? = "Middle",
    @SerializedName("death_runs") val deathRuns: Int = 0,
    @SerializedName("confidence") val confidence: Int = 0
)

data class PredictionDetail(
    @SerializedName("runs") val runs: Int = 0,
    @SerializedName("confidence") val confidence: Int = 0
)

data class PartnershipForecast(
    @SerializedName("runs") val runs: Int = 0,
    @SerializedName("chance") val chance: String? = "low"
)

data class BatsmanForecast(
    @SerializedName("name") val name: String?,
    @SerializedName("final_runs") val final_runs: Int = 0,
    @SerializedName("boundary_percent") val boundary_percent: Int = 0,
    @SerializedName("out_risk") val out_risk: Int = 0,
    // Add these for backward compatibility if used in PredictionsScreen.kt
    @SerializedName("finalRuns") val finalRuns: Int = 0,
    @SerializedName("boundaryPercent") val boundaryPercent: Int = 0,
    @SerializedName("outRisk") val outRisk: Int = 0
)

data class EndMatchRequest(
    @SerializedName("match_id") val matchId: String,
    @SerializedName("winner") val winner: String,
    @SerializedName("result") val result: String
)
