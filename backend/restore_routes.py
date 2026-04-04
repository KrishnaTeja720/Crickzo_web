import os
import numpy as np

path = r"d:\website-frontend\backend\routes.py"
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_predict = [
    "@routes.route(\"/predict\", methods=[\"POST\"])\n",
    "def predict():\n",
    "    if model is None: return jsonify({\"error\": \"Model missing\"}), 500\n",
    "    data = request.json\n",
    "    # Model expects [runs_needed, balls_left, wickets_remaining]\n",
    "    features = np.array([[data.get(\"runs_left\", 0), data.get(\"balls_left\", 0), data.get(\"wickets\", 0)]])\n",
    "    try:\n",
    "        prob = model.predict_proba(features)[0][1]\n",
    "        return jsonify({\"win_probability\": round(prob * 100, 2)})\n",
    "    except Exception as e:\n",
    "        print(f\"[ERROR] Predict route failed: {e}\")\n",
    "        return jsonify({\"win_probability\": 50.0, \"error\": str(e)})\n",
    "\n"
]

final_lines = lines[:1803] + new_predict
final_lines.extend(lines[1818:2131])

new_scorecard_exc = [
    "    except Exception as e:\n",
    "        print(f\"SCORECARD ERROR: {e}\")\n",
    "        return jsonify({\"error\": str(e)}), 500\n",
    "\n"
]
final_lines.extend(new_scorecard_exc)
final_lines.extend(lines[2138:2233])

new_end = [
    "    result = []\n",
    "    for m in matches:\n",
    "        result.append({\n",
    "            \"match_id\": m[0],\n",
    "            \"team_a\": m[1],\n",
    "            \"team_b\": m[2],\n",
    "            \"venue\": m[3],\n",
    "            \"winner\": m[4],\n",
    "            \"format\": m[5]\n",
    "        })\n",
    "    return jsonify(result)\n"
]
final_lines.extend(new_end)

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(final_lines)
print("Restored!")
