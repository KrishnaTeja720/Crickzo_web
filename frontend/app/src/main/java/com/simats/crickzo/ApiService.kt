package com.simats.crickzo

import retrofit2.Response
import retrofit2.http.*

interface ApiService {
    // Auth
    @POST("signup")
    suspend fun signup(@Body request: SignupRequest): Response<SignupResponse>

    @POST("login")
    suspend fun login(@Body request: LoginRequest): Response<LoginResponse>

    @POST("forgot_password")
    suspend fun forgotPassword(@Body request: ForgotPasswordRequest): Response<ForgotPasswordResponse>

    @POST("verify_otp")
    suspend fun verifyOtp(@Body request: VerifyOtpRequest): Response<VerifyOtpResponse>

    @POST("reset_password")
    suspend fun resetPassword(@Body request: ResetPasswordRequest): Response<ResetPasswordResponse>

    @POST("resend_otp")
    suspend fun resendOtp(@Body request: ResendOtpRequest): Response<ResendOtpResponse>

    @POST("change_password")
    suspend fun changePassword(@Body request: ChangePasswordRequest): Response<GenericResponse>

    @GET("user/profile/{userId}")
    suspend fun getUserProfile(@Path("userId") userId: String): Response<UserProfileResponse>

    // Matches
    @POST("match/create")
    suspend fun createMatch(
        @Body request: CreateMatchRequest
    ): Response<CreateMatchResponse>

    @GET("matches/live")
    suspend fun getLiveMatches(
        @Query("user_id") userId: Int
    ): Response<List<LiveMatchData>>

    @GET("matches/completed")
    suspend fun getCompletedMatches(
        @Query("user_id") userId: Int
    ): Response<List<CompletedMatchInfo>>

    @GET("match/details/{match_id}")
    suspend fun getMatchDetails(@Path("match_id") matchId: String): Response<MatchDetailsResponse>

    @POST("match/end")
    suspend fun endMatch(@Body request: EndMatchRequest): Response<GenericResponse>

    // Players
    @POST("match/setup")
    suspend fun matchSetup(@Body request: MatchSetupRequest): Response<GenericResponse>

    @POST("match/start")
    suspend fun startMatch(@Body request: StartMatchRequest): Response<GenericResponse>

    @GET("match/players/{matchId}")
    suspend fun getMatchPlayers(@Path("matchId") matchId: String): Response<List<Player>>

    // Scoring
    @POST("match/ball")
    suspend fun submitBall(@Body request: BallInputRequest): Response<GenericResponse>

    @DELETE("match/undo/{match_id}")
    suspend fun undoBall(
        @Path("match_id") matchId: String
    ): Response<GenericResponse>

    @GET("match/score/{match_id}")
    suspend fun getScoreboard(
        @Path("match_id") matchId: String,
        @Query("innings") innings: Int
    ): Response<ScoreResponse>

    @GET("match/batsmen/{match_id}")
    suspend fun getBatsmenStats(@Path("match_id") matchId: String): Response<List<BatsmanStat>>

    @GET("match/bowler/{match_id}")
    suspend fun getBowlerStats(@Path("match_id") matchId: String): Response<List<BowlerStat>>

    @GET("match/partnership/{match_id}")
    suspend fun getPartnership(
        @Path("match_id") matchId: String,
        @Query("innings") innings: Int
    ): Response<PartnershipResponse>

    @GET("match/last6/{match_id}")
    suspend fun getLast6Balls(
        @Path("match_id") matchId: String,
        @Query("innings") innings: Int
    ): Response<List<String>>

    // Predictions
    @GET("match/predictions/{match_id}")
    suspend fun getMatchPredictions(@Path("match_id") matchId: String): Response<MatchPredictions>
}
