import re

file_path = 'd:/film eleştirmen/frontend/src/pages/QuizDuello.jsx'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add Lucide icons: Zap, Snowflake, Dice5
content = content.replace("Swords, Trophy, Users, Check, X, ChevronLeft, Clock,", "Swords, Trophy, Users, Check, X, ChevronLeft, Clock, Zap, Snowflake, Dices, Scissors,")

joker_ui = """
      {/* Jokers & Streak */}
      <div className="flex items-center justify-between px-2">
        {/* Streak */}
        <div className="flex items-center gap-1.5">
          <Zap size={16} className={my_streak >= 2 ? "text-amber animate-pulse" : "text-amber/40"} />
          <span className={`text-xs font-bold ${my_streak >= 2 ? "text-amber" : "text-fg-subtle"}`}>
            Seri: {my_streak || 0} {my_streak >= 2 && <span className="text-amber/80 text-[10px] ml-1">(x1.5 Puan)</span>}
          </span>
        </div>

        {/* Jokerler */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => handleJoker('fifty_fifty')}
            disabled={my_answer || jokerLoading || timeLeft <= 0 || (player_jokers?.fifty_fifty !== undefined)}
            className={`p-1.5 rounded-lg border transition-all flex items-center justify-center
              ${player_jokers?.fifty_fifty !== undefined
                ? 'border-white/5 bg-surface-2/20 text-fg-muted opacity-50'
                : 'border-amber/30 bg-amber-900/30 text-amber hover:bg-amber-900/50'
              }`}
            title="Yarı Yarıya (%50)"
          >
            <Scissors size={14} />
          </button>
          
          <button
            onClick={() => handleJoker('freeze_time')}
            disabled={my_answer || jokerLoading || timeLeft <= 0 || (player_jokers?.freeze_time !== undefined)}
            className={`p-1.5 rounded-lg border transition-all flex items-center justify-center
              ${player_jokers?.freeze_time !== undefined
                ? 'border-white/5 bg-surface-2/20 text-fg-muted opacity-50'
                : 'border-blue-500/30 bg-blue-900/30 text-blue-400 hover:bg-blue-900/50'
              }`}
            title="Zamanı Dondur (+10s)"
          >
            <Snowflake size={14} />
          </button>

          <button
            onClick={() => handleJoker('double_chance')}
            disabled={my_answer || jokerLoading || timeLeft <= 0 || (player_jokers?.double_chance !== undefined)}
            className={`p-1.5 rounded-lg border transition-all flex items-center justify-center
              ${player_jokers?.double_chance !== undefined
                ? 'border-white/5 bg-surface-2/20 text-fg-muted opacity-50'
                : 'border-emerald/30 bg-emerald-900/30 text-emerald hover:bg-emerald-900/50'
              }`}
            title="Çifte Şans"
          >
            <Dices size={14} />
          </button>
        </div>
      </div>

"""

content = re.sub(r'\{\/\* Soru metni \*\/\}\s*<motion\.p', joker_ui.strip() + '\n\n      {/* Soru metni */}\n      <motion.p', content)

old_option = """          return (
            <motion.button
              key={`${question.index}-${i}`}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.2, delay: i * 0.05 }}
              onClick={() => handleSelect(option)}
              disabled={!!my_answer || !!selected || timeLeft <= 0}
              whileTap={!my_answer && !selected && timeLeft > 0 ? { scale: 0.97 } : {}}
              className={`w-full px-4 py-3 rounded-xl border text-sm text-left transition-colors duration-200 ${
                isCorrect || (isCorrectAnswer && !isMyPick)"""

option_logic = """          const isEliminated = eliminatedOptions.includes(option);

          return (
            <motion.button
              key={`${question.index}-${i}`}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.2, delay: i * 0.05 }}
              onClick={() => handleSelect(option)}
              disabled={!!my_answer || !!selected || timeLeft <= 0 || isEliminated}
              whileTap={!my_answer && !selected && timeLeft > 0 && !isEliminated ? { scale: 0.97 } : {}}
              className={`w-full px-4 py-3 rounded-xl border text-sm text-left transition-colors duration-200 ${
                isEliminated ? 'opacity-20 pointer-events-none' :
                isCorrect || (isCorrectAnswer && !isMyPick)"""

content = content.replace(old_option, option_logic)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Patch UI done.")
