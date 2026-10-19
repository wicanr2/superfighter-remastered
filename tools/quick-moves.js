/* 可撤回設定原型。招式名稱與指令依手冊；沒有遊戲注入或已驗證時序。 */
(function (root) {
  "use strict";
  const slots = ["R1", "R2", "L1", "L2"];
  const catalog = [
    ["jaan", "斬", [["天雷斬", "→↘↓＋拳"], ["旋風腿", "↓↙←＋腳"], ["鐵頭功", "蹲蓄力，跳＋腳"], ["過肩摔", "移動＋拳（近身）"]]],
    ["sarkov", "薩爾可夫", [["碎頭捶", "拳＋腳（近身）"], ["空抓", "方向＋腳（空中）"], ["折腰摔", "移動＋拳＋腳（近身）"], ["迴旋拋", "移動＋拳（近身）"]]],
    ["bullet", "子彈", [["蜻蜓點水", "↓↘→＋腳"], ["連環踢", "後蓄力，前＋腳"], ["滾踢", "↓↙←＋腳"], ["碎頭摔", "移動＋拳（近身）"]]],
    ["phoenix", "鳳凰", [["火鳳凰", "後蓄力，前＋拳＋腳"], ["迴旋腳刀", "←↙↓＋腳"], ["倒掛金鉤", "↓↙←＋腳"], ["蠍子尾", "↓＋拳＋腳（近身）"], ["反身摔", "移動＋拳（近身）"]]],
    ["frank", "法蘭克", [["氣動拳", "↓↘→＋拳"], ["旋風拳", "←↓↙＋拳"], ["翔龍拳", "→↓↘＋拳"], ["空旋摔", "移動＋拳＋腳（近身）"]]],
    ["onimaru", "鬼丸", [["旋風忍術", "拳＋腳"], ["龜忍術", "後蓄力，前＋拳或腳"], ["空摔", "方向＋拳（空中）"], ["鬼啃頭", "移動＋拳（近身）"]]],
    ["lan", "嵐", [["劈掛掌", "後蓄力，前＋拳"], ["龍捲風", "↓↙←＋腳"], ["雙截踢", "↓↘→＋腳"], ["大佛腳", "拳＋腳（近身）"], ["大車輪", "移動＋拳（近身）"]]],
    ["kim", "金太極", [["太極刀光", "↓↘→＋拳"], ["太極波", "後蓄力，前＋拳"], ["疾刺", "後蓄力，前＋腳"], ["八卦掌", "↓↙←＋拳"], ["空拋", "移動＋拳（近身）"]]]
  ].map(([id, name, moves]) => ({ id, name, moves: moves.map(([name, command], index) => ({ id: String(index + 1), name, command })) }));
  function character(id) {
    const value = catalog.find(c => c.id === id);
    if (!value) throw new Error("未知角色");
    return value;
  }
  function defaults() {
    return Object.fromEntries(catalog.map(c => [c.id, Object.fromEntries(slots.map((slot, i) => [slot, c.moves[i]?.id || ""]))]));
  }
  function normalize(input) {
    const output = defaults();
    if (!input || typeof input !== "object" || Array.isArray(input)) return output;
    for (const c of catalog) {
      if (!Object.hasOwn(input, c.id)) continue;
      const mapping = input[c.id];
      if (!mapping || typeof mapping !== "object" || Array.isArray(mapping)) continue;
      for (const slot of slots) {
        if (!Object.hasOwn(mapping, slot)) continue;
        const value = mapping[slot];
        output[c.id][slot] = value === "" || c.moves.some(m => m.id === value) ? value : "";
      }
    }
    return output;
  }
  function resolve(profiles, id, slot, facing) {
    if (!slots.includes(slot)) throw new Error("只接受四個快捷位置");
    if (facing !== "right" && facing !== "left") throw new Error("朝向未知，不猜測左右");
    const c = character(id), moveId = profiles[id]?.[slot];
    const move = c.moves.find(m => m.id === moveId);
    if (!move) return null;
    const flipped = {"←":"→", "→":"←", "↙":"↘", "↘":"↙", "↖":"↗", "↗":"↖"};
    return {...move, character: c.name, slot, command: facing === "right" ? move.command : move.command.replace(/[←→↙↘↖↗]/g, ch => flipped[ch]),
      status: "manual candidate; timing and game injection unverified"};
  }
  // 每次按下只回報一次。保持按住不連發；換角色、裝置或頁面失焦時重置。
  function edgeTracker() {
    let held = new Set();
    return { update(pressed) {
      const next = new Set(pressed.filter(slot => slots.includes(slot)));
      const rising = slots.filter(slot => next.has(slot) && !held.has(slot));
      held = next;
      return rising;
    }, reset() { held.clear(); } };
  }
  const api = {slots, catalog, character, defaults, normalize, resolve, edgeTracker};
  root.QuickMoves = api;
  if (typeof module !== "undefined" && module.exports) module.exports = api;
})(typeof globalThis !== "undefined" ? globalThis : this);
