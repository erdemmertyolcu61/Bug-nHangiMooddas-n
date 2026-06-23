import re

file_path = 'd:/film eleştirmen/backend/routers/quiz.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add /joker endpoint
joker_endpoint = """
@router.post("/rooms/{room_id}/joker")
async def use_joker(room_id: str, body: JokerBody, user: dict = Depends(verify_user)):
    me = user["user_id"]
    async with _db_conn(cache.db_path, user_data=True) as db:
        room = await _get_room(db, room_id)
        if room["status"] != "PLAYING":
            raise HTTPException(status_code=400, detail="Oyun aktif değil")
        if me not in (room["creator_id"], room["opponent_id"]):
            raise HTTPException(status_code=403, detail="Bu odada değilsin")
        if body.question_index != room["current_question"]:
            raise HTTPException(status_code=400, detail="Yanlış soru index'i")
        
        jokers = json.loads(room.get("player_jokers") or "{}")
        my_jokers = jokers.setdefault(str(me), {})
        
        if body.joker_type in my_jokers:
            raise HTTPException(status_code=400, detail="Bu joker zaten kullanılmış")
            
        my_jokers[body.joker_type] = body.question_index
        
        await db.execute("UPDATE quiz_rooms SET player_jokers = ? WHERE id = ?", (json.dumps(jokers), room_id))
        await db.commit()
        
        eliminated = []
        if body.joker_type == "fifty_fifty":
            cur_q = await db.execute("SELECT options, correct_answer FROM quiz_questions WHERE room_id = ? AND question_index = ?", (room_id, body.question_index))
            q_row = await cur_q.fetchone()
            if q_row:
                options = json.loads(q_row[0])
                correct = q_row[1]
                wrong_opts = [o for o in options if o != correct]
                if len(wrong_opts) >= 2:
                    import random
                    eliminated = random.sample(wrong_opts, 2)
                    
        return {"ok": True, "eliminated": eliminated}

@router.post("/rooms/{room_id}/answer")
"""
content = re.sub(r'@router\.post\("/rooms/\{room_id\}/answer"\)', joker_endpoint.strip(), content)

# 2. Update poll_room response
poll_update = """                cur_streak = await db.execute("SELECT is_correct FROM quiz_answers WHERE room_id = ? AND user_id = ? ORDER BY question_index ASC", (room_id, me))
                streak_rows = await cur_streak.fetchall()
                my_streak = 0
                for r in streak_rows:
                    if r[0]: my_streak += 1
                    else: my_streak = 0
                    
                jokers_dict = json.loads(room.get("player_jokers") or "{}")

                response.update({
                    "current_question": q_idx,
                    "total_questions": QUESTIONS_PER_GAME,
                    "question": question_data,
                    "my_answer": my_answer,
                    "my_streak": my_streak,
                    "player_jokers": jokers_dict,
                    "opponent_answered": opp_answered,
                    "scores": {"""

content = re.sub(r'response\.update\(\{[\s]*"current_question": q_idx,[\s]*"total_questions": QUESTIONS_PER_GAME,[\s]*"question": question_data,[\s]*"my_answer": my_answer,[\s]*"opponent_answered": opp_answered,[\s]*"scores": \{', poll_update.strip(), content)

# 3. Update submit_answer logic
old_submit = """        existing = await db.execute(
            "SELECT id FROM quiz_answers WHERE room_id = ? AND question_index = ? AND user_id = ?",
            (room_id, body.question_index, me),
        )
        if await existing.fetchone():
            raise HTTPException(status_code=400, detail="Bu soruyu zaten cevapladın")

        started_at = room.get("question_started_at", "")
        elapsed_ms = QUESTION_TIME_MS
        if started_at:
            started_ms = int(datetime.fromisoformat(started_at).timestamp() * 1000)
            elapsed_ms = min(QUESTION_TIME_MS, max(0, _now_ms() - started_ms))

        if elapsed_ms > QUESTION_TIME_MS + 2000:
            raise HTTPException(status_code=400, detail="Süre doldu")

        cur_q = await db.execute(
            "SELECT correct_answer FROM quiz_questions WHERE room_id = ? AND question_index = ?",
            (room_id, body.question_index),
        )
        q_row = await cur_q.fetchone()
        if not q_row:
            raise HTTPException(status_code=500, detail="Soru bulunamadı")

        correct_answer = q_row[0]
        is_correct = body.selected_answer == correct_answer
        score = _calculate_score(elapsed_ms) if is_correct else 0

        await db.execute(
            \"\"\"INSERT INTO quiz_answers
               (room_id, question_index, user_id, selected_answer, is_correct, elapsed_ms, score)
               VALUES (?, ?, ?, ?, ?, ?, ?)\"\"\",
            (room_id, body.question_index, me, body.selected_answer, int(is_correct), elapsed_ms, score),
        )"""

new_submit = """        jokers = json.loads(room.get("player_jokers") or "{}")
        my_jokers = jokers.get(str(me), {})
        
        has_freeze_time = my_jokers.get("freeze_time") == body.question_index
        max_time_ms = QUESTION_TIME_MS + (10000 if has_freeze_time else 0)
        
        existing_cur = await db.execute(
            "SELECT id, is_correct FROM quiz_answers WHERE room_id = ? AND question_index = ? AND user_id = ?",
            (room_id, body.question_index, me),
        )
        existing = await existing_cur.fetchone()
        
        has_double_chance = my_jokers.get("double_chance") == body.question_index
        
        if existing:
            if existing[1] == 1 or not has_double_chance:
                raise HTTPException(status_code=400, detail="Bu soruyu zaten cevapladın")
        
        started_at = room.get("question_started_at", "")
        elapsed_ms = max_time_ms
        if started_at:
            started_ms = int(datetime.fromisoformat(started_at).timestamp() * 1000)
            elapsed_ms = min(max_time_ms, max(0, _now_ms() - started_ms))

        if elapsed_ms > max_time_ms + 2000:
            raise HTTPException(status_code=400, detail="Süre doldu")

        cur_q = await db.execute(
            "SELECT correct_answer FROM quiz_questions WHERE room_id = ? AND question_index = ?",
            (room_id, body.question_index),
        )
        q_row = await cur_q.fetchone()
        if not q_row:
            raise HTTPException(status_code=500, detail="Soru bulunamadı")

        correct_answer = q_row[0]
        is_correct = body.selected_answer == correct_answer
        
        cur_streak = await db.execute("SELECT is_correct FROM quiz_answers WHERE room_id = ? AND user_id = ? AND question_index < ? ORDER BY question_index ASC", (room_id, me, body.question_index))
        streak_rows = await cur_streak.fetchall()
        streak_count = 0
        for r in streak_rows:
            if r[0]: streak_count += 1
            else: streak_count = 0
            
        base_score = _calculate_score(elapsed_ms) if is_correct else 0
        if existing and is_correct:
            base_score = 10 # Cezalı puan
            
        score = base_score
        is_combo = False
        if is_correct and streak_count >= 2:
            score = int(score * 1.5)
            is_combo = True
            
        if existing:
            await db.execute(
                "UPDATE quiz_answers SET selected_answer = ?, is_correct = ?, elapsed_ms = ?, score = ? WHERE id = ?",
                (body.selected_answer, int(is_correct), elapsed_ms, score, existing[0]),
            )
        else:
            await db.execute(
                \"\"\"INSERT INTO quiz_answers
                   (room_id, question_index, user_id, selected_answer, is_correct, elapsed_ms, score)
                   VALUES (?, ?, ?, ?, ?, ?, ?)\"\"\",
                (room_id, body.question_index, me, body.selected_answer, int(is_correct), elapsed_ms, score),
            )"""

content = content.replace(old_submit, new_submit)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Patching quiz.py done.")
