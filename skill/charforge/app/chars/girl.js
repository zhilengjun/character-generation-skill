/* =============================================================================
 * charforge 角色存档 —— 女孩（chibi-3head-warmline-128）· 套装变体格式 v2
 * 画布 128 x 128，角色总高 128px。
 * 数据模型：
 *   headsets  头部套装（含发型）        —— 单选 1 套
 *   faces     表情（绝对坐标，画在头上） —— 单选 1 个
 *   bodies    身体套装 {legL,legR,torso,armL,armR} 5 件 —— 单选 1 套，整体替换
 *   attachments 挂件 {cat,slot,offset,z,draw}       —— 跨分类复选，分类内单选（可反选）
 * 风格：平涂无描边；部件靠色差区分；鞋为圆角矩形；上衣斜肩+圆领
 * ========================================================================== */
(function (global) {
  'use strict';

  /* --------------------------------------------------- 绘图原语（每文件自带） */
  var LINE = '#4A3B42';        // 五官/细节线色（平涂风，不做轮廓描边）

  function stroked(d, w, col, extra) {
    return '<path d="' + d + '" fill="none" stroke="' + col + '" stroke-width="' + w +
      '" stroke-linecap="round" stroke-linejoin="round"' + (extra || '') + '/>';
  }
  /** 圆头肢体：无描边，纯色条（相邻部件靠色差区分） */
  function limb(d, w, fill) {
    return stroked(d, w, fill);
  }
  /** 平涂形状（无描边） */
  function shape(d, fill) {
    return '<path d="' + d + '" fill="' + fill + '"/>';
  }
  function ell(cx, cy, rx, ry, fill) {
    return '<ellipse cx="' + cx + '" cy="' + cy + '" rx="' + rx + '" ry="' + ry +
      '" fill="' + fill + '"/>';
  }
  function circ(cx, cy, r, fill) {
    return '<circle cx="' + cx + '" cy="' + cy + '" r="' + r + '" fill="' + fill + '"/>';
  }
  /** 圆角矩形（鞋等平底部件） */
  function rrect(x, y, w, h, r, fill) {
    return '<rect x="' + x + '" y="' + y + '" width="' + w + '" height="' + h +
      '" rx="' + r + '" ry="' + r + '" fill="' + fill + '"/>';
  }
  function dot(cx, cy, r, fill) {
    return '<circle cx="' + cx + '" cy="' + cy + '" r="' + r + '" fill="' + fill + '"/>';
  }

  var P = {
    id: 'girl',
    name: '女孩',
    style: 'chibi-3head-warmline-128',
    canvas: { w: 128, h: 128 },
    height: 128,
    palette: {
      skin: '#FFCFAB', skinS: '#F2B489', hair: '#A9673C',
      top: '#B48AD6', topS: '#9A72C2', topD: '#8F63B8', bot: '#4E6B93', botD: '#3B5273',
      dressP: '#F2A7C3', dressD: '#E0567E',
      shoe: '#8A5A3C', sock: '#FFFFFF', blush: '#FF7A4D',
      hat: '#E86A8E', berry: '#FF4D6D'
    },
    /* 挂点：挂件以 anchor+offset 为局部原点作画（slot-local 坐标，y 向下） */
    anchors: {
      head: [64, 21], body: [64, 72], back: [64, 72],
      hand_l: [40.5, 89.5], hand_r: [87.5, 89.5],
      foot_l: [54, 120], foot_r: [74, 120]
    },

    /* ------------------------------------------------ 头部套装（单选 1 套，含发型） */
    headsets: [
      {
        id: 'bob', name: '短发·鬓发', z: 5,
        draw: function (p) {
          var s = ell(64, 33, 22, 22, p.skin);
          // 前发：发盖 + 两侧鬓发（20260910 女友前发 ×0.61 换算）
          s += shape('M41.4 34.4 C41.4 19.4 51.2 10 64 10 ' +
            'C76.8 10 86.6 19.4 86.6 34.4 ' +
            'C82.3 28.3 76.2 25.9 70.1 28.3 ' +
            'C66.4 23.4 59.1 23.4 55.5 28.3 ' +
            'C49.4 25.9 44.5 29.6 41.4 34.4 Z', p.hair);
          s += shape('M43.9 35.1 C36.2 42.4 36.8 52.2 42.6 63.2 ' +
            'C46.7 53.4 47.4 42.4 46.1 35.7 Z', p.hair);
          s += shape('M84.1 35.1 C91.8 42.4 91.2 52.2 85.4 63.2 ' +
            'C81.3 53.4 80.6 42.4 81.9 35.7 Z', p.hair);
          return s;
        }
      },
      {
        id: 'twin', name: '双马尾', z: 5,
        draw: function (p) {
          var s = ell(64, 33, 22, 22, p.skin);
          // 两侧马尾（在头后层，先画）+ 与 bob 相同的前发
          s += shape('M43.5 30 C33 31 27.5 42 30.5 53 ' +
            'C32.5 59 39.5 59.5 42.5 53.5 C39 46 40 36 43.5 30 Z', p.hair);
          s += shape('M84.5 30 C95 31 100.5 42 97.5 53 ' +
            'C95.5 59 88.5 59.5 85.5 53.5 C89 46 88 36 84.5 30 Z', p.hair);
          s += shape('M41.4 34.4 C41.4 19.4 51.2 10 64 10 ' +
            'C76.8 10 86.6 19.4 86.6 34.4 ' +
            'C82.3 28.3 76.2 25.9 70.1 28.3 ' +
            'C66.4 23.4 59.1 23.4 55.5 28.3 ' +
            'C49.4 25.9 44.5 29.6 41.4 34.4 Z', p.hair);
          s += shape('M43.9 35.1 C36.2 42.4 36.8 52.2 42.6 63.2 ' +
            'C46.7 53.4 47.4 42.4 46.1 35.7 Z', p.hair);
          s += shape('M84.1 35.1 C91.8 42.4 91.2 52.2 85.4 63.2 ' +
            'C81.3 53.4 80.6 42.4 81.9 35.7 Z', p.hair);
          return s;
        }
      }
    ],

    /* ------------------------------------------------ 表情（单选 1 个，绝对坐标） */
    faces: [
      {
        id: 'smile', name: '微笑', z: 6,
        draw: function (p) {
          var s = dot(55.5, 35.6, 3, LINE) + dot(72.5, 35.6, 3, LINE);
          s += dot(54.7, 34.6, 1.1, '#FFFFFF') + dot(71.7, 34.6, 1.1, '#FFFFFF');
          s += stroked('M61.5 45.5 Q64 47.6 66.5 45.5', 1.9, LINE);
          s += dot(51, 41.5, 2.6, p.blush) + dot(77, 41.5, 2.6, p.blush);
          return s;
        }
      },
      {
        id: 'wink', name: '眨眼', z: 6,
        draw: function (p) {
          var s = stroked('M51.2 36.9 Q55.5 31.3 59.8 36.9', 2.1, LINE) +
            stroked('M68.2 36.5 L77 36.5', 2.1, LINE) +
            stroked('M77 36.5 L79.5 34', 1.6, LINE);
          s += dot(64, 45, 2.2, LINE);
          s += dot(52.5, 40.8, 3, p.blush) + dot(75.5, 40.8, 3, p.blush);
          return s;
        }
      }
    ],

    /* ------------------------------------------------ 身体套装（单选 1 套 = 5 件整体替换） */
    bodies: [
      {
        id: 'purple', name: '紫上衣·蓝短裙',
        legL: {
          z: 1,
          draw: function (p) {
            return limb('M57 96 L55.5 115', 9, p.skin) + rrect(45.5, 114.5, 17, 11, 5.5, p.shoe);
          }
        },
        legR: {
          z: 1,
          draw: function (p) {
            return limb('M71 96 L72.5 115', 9, p.skin) + rrect(65.5, 114.5, 17, 11, 5.5, p.shoe);
          }
        },
        torso: {
          z: 3,
          draw: function (p) {
            return shape('M58 47 L70 47 L70 58 L58 58 Z', p.skinS) +               // 脖子（12 宽）
              // 上衣：斜肩（肩点 47/81@67 → 颈侧 58/70@58）
              shape('M47 67 C51 60 55.5 58 58 58 L70 58 ' +
                'C72.5 58 77 60 81 67 L79 84 C71 87.5 57 87.5 49 84 Z', p.top) +
              // 衣领：白色圆领环绕颈根
              shape('M55.5 57.5 C58 62.5 70 62.5 72.5 57.5 ' +
                'C74.5 60 73.5 63.5 70.5 65 C66.5 66.8 61.5 66.8 57.5 65 ' +
                'C54.5 63.5 53.5 60 55.5 57.5 Z', '#F7F1E8') +
              shape('M49 81 L79 81 L86 94.5 C76 98.5 52 98.5 42 94.5 Z', p.bot) +  // 短裙
              stroked('M57 86 L54 96.5', 1.6, p.botD) +
              stroked('M71 86 L74 96.5', 1.6, p.botD);
          }
        },
        armL: {
          z: 4,
          draw: function (p) {
            return limb('M48.5 64 L44 76', 8, p.topS) +
              limb('M44 76 L41 87', 6.5, p.skin) + circ(40.5, 89.5, 4.3, p.skin);
          }
        },
        armR: {
          z: 4,
          draw: function (p) {
            return limb('M79.5 64 L84 76', 8, p.topS) +
              limb('M84 76 L87 87', 6.5, p.skin) + circ(87.5, 89.5, 4.3, p.skin);
          }
        }
      },
      {
        id: 'pink', name: '粉连衣裙·白袜',
        legL: {
          z: 1,
          draw: function (p) {
            return limb('M57 96 L55.5 113', 9, p.skin) +
              rrect(46, 107.5, 16, 8, 4, p.sock) +
              rrect(45.5, 114.5, 17, 11, 5.5, p.shoe);
          }
        },
        legR: {
          z: 1,
          draw: function (p) {
            return limb('M71 96 L72.5 113', 9, p.skin) +
              rrect(66, 107.5, 16, 8, 4, p.sock) +
              rrect(65.5, 114.5, 17, 11, 5.5, p.shoe);
          }
        },
        torso: {
          z: 3,
          draw: function (p) {
            return shape('M58 47 L70 47 L70 58 L58 58 Z', p.skinS) +
              // 连衣裙：斜肩 + 收腰 + 展摆到 y≈99
              shape('M47 67 C51 60 55.5 58 58 58 L70 58 ' +
                'C72.5 58 77 60 81 67 L84.5 99 C74 103.5 54 103.5 43.5 99 Z', p.dressP) +
              shape('M55.5 57.5 C58 62.5 70 62.5 72.5 57.5 ' +
                'C74.5 60 73.5 63.5 70.5 65 C66.5 66.8 61.5 66.8 57.5 65 ' +
                'C54.5 63.5 53.5 60 55.5 57.5 Z', '#F7F1E8') +
              stroked('M46.5 80 L81.5 80', 3.2, p.dressD);                         // 腰带
          }
        },
        armL: {
          z: 4,
          draw: function (p) {
            return limb('M48.5 64 L44 76', 8, p.dressD) +
              limb('M44 76 L41 87', 6.5, p.skin) + circ(40.5, 89.5, 4.3, p.skin);
          }
        },
        armR: {
          z: 4,
          draw: function (p) {
            return limb('M79.5 64 L84 76', 8, p.dressD) +
              limb('M84 76 L87 87', 6.5, p.skin) + circ(87.5, 89.5, 4.3, p.skin);
          }
        }
      }
    ],

    /* ------------------------------------------------ 挂件（跨分类复选，分类内单选） */
    attachments: [
      {
        id: 'hat_beret', name: '贝雷帽', cat: '帽子', slot: 'head', offset: [0, 0], z: 7.5,
        draw: function (p) {
          return shape('M-24 0 C-25 -8 -13 -13.5 0 -13 C13 -12.5 23 -7 22.5 0.5 ' +
            'C10 -3.5 -11 -3.5 -24 0 Z', p.hat) +
            circ(0, -13.5, 2.6, p.hat, 2);
        }
      },
      {
        id: 'band_berry', name: '草莓发箍', cat: '帽子', slot: 'head', offset: [0, 0], z: 7.5,
        draw: function (p) {
          return stroked('M-19.5 -1.5 C-12 -10.5 12 -10.5 19.5 -1.5', 4.5, p.hat) +
            circ(-17, -2.5, 3, p.berry) + circ(17, -2.5, 3, p.berry);
        }
      },
      {
        id: 'glasses_round', name: '圆框眼镜', cat: '眼镜', slot: 'head', offset: [0, 12], z: 7.6,
        draw: function () {
          return '<g fill="none" stroke="' + LINE + '" stroke-width="2">' +
            '<circle cx="-8.5" cy="3" r="6.3"/><circle cx="8.5" cy="3" r="6.3"/>' +
            '<path d="M-2.2 3 L2.2 3"/><path d="M-14.8 2 L-21 -0.5"/><path d="M14.8 2 L21 -0.5"/>' +
            '</g>' +
            '<circle cx="-8.5" cy="3" r="6.3" fill="#FFFFFF" opacity="0.16"/>' +
            '<circle cx="8.5" cy="3" r="6.3" fill="#FFFFFF" opacity="0.16"/>';
        }
      },
      {
        id: 'wand_star', name: '星星法杖', cat: '武器', slot: 'hand_r', offset: [0, 0], z: 6,
        draw: function (p) {
          return stroked('M3 7 L15 -23', 3.2, '#8A5A3C') +
            stroked('M5 1 L9 -9', 4.4, '#6B4A2F') +
            shape('M16 -31.5 L18 -26.5 L23.2 -26 L19.4 -22.4 L20.4 -17.2 L16 -19.8 ' +
              'L11.6 -17.2 L12.6 -22.4 L8.8 -26 L14 -26.5 Z', '#FFC75F', 2);
        }
      }
    ]
  };

  global.registerCharacter(P);
})(typeof window !== 'undefined' ? window : globalThis);
