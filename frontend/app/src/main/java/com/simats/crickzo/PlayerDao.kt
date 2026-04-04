package com.simats.crickzo

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query

@Dao
interface PlayerDao {
    @Query("SELECT * FROM players WHERE matchId = :matchId")
    suspend fun getPlayersByMatchId(matchId: String): List<PlayerEntity>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertPlayers(players: List<PlayerEntity>)

    @Query("DELETE FROM players WHERE matchId = :matchId")
    suspend fun deletePlayersByMatchId(matchId: String)
}
