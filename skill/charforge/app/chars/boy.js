/* =============================================================================
 * charforge 角色存档 —— 男孩（chibi-3head-warmline-128）· 套装变体格式 v2
 * 数据模型同 girl.js：headsets / faces / bodies / attachments(cat)
 * 与女孩同 style：默认套装下各基础件 bbox 尺寸差异控制在 20% 以内（手臂统一垂放姿态）
 * 风格：平涂无描边；部件靠色差区分；鞋为圆角矩形；外套斜肩+衬衫领
 * ========================================================================== */
(function (global) {
  'use strict';

  /* --------------------------------------------------- 绘图原语（每文件自带） */
  var LINE = '#4A3B42';

  function stroked(d, w, col, extra) {
    return '<path d="' + d + '" fill="none" stroke="' + col + '" stroke-width="' + w +
      '" stroke-linecap="round" stroke-linejoin="round"' + (extra || '') + '/>';
  }
  function limb(d, w, fill) {
    return stroked(d, w, fill);
  }
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
  function rrect(x, y, w, h, r, fill) {
    return '<rect x="' + x + '" y="' + y + '" width="' + w + '" height="' + h +
      '" rx="' + r + '" ry="' + r + '" fill="' + fill + '"/>';
  }
  function dot(cx, cy, r, fill) {
    return '<circle cx="' + cx + '" cy="' + cy + '" r="' + r + '" fill="' + fill + '"/>';
  }

  var P = {
    id: 'boy',
    name: '男孩',
    style: 'chibi-3head-warmline-128',
    canvas: { w: 128, h: 128 },
    height: 128,
    palette: {
      skin: '#F7C49B', skinS: '#E9AC80', hair: '#966E67',
      jacket: '#C9A66B', jacketD: '#A3824E', shirt: '#7A8CA8',
      pants: '#47618C', shoe: '#2A2025', sock: '#FFFFFF', blush: '#FF7A4D',
      tee: '#5FA8D3', teeD: '#4A8CB8', shorts: '#6B7B8C',
      cap: '#FF4D6D', capD: '#D63A5A',
      cape: '#5FD3A6', capeD: '#3FAE85'
    },
    anchors: {
      head: [64, 21], body: [64, 72], back: [64, 74],
      hand_l: [40.5, 89.5], hand_r: [87.5, 89.5],
      foot_l: [55, 118], foot_r: [73, 118]
    },

    /* ------------------------------------------------ 头部套装（单选 1 套，含发型） */
    headsets: [
      {
        id: 'bowl', name: '中分碗形', z: 5,
        draw: function (p) {
          var s = ell(64, 33, 22, 22, p.skin);
          // 中分碗形短发（两侧发梢锯齿；头部下移 3 贴近身体）
          s += shape('M35.9 40.1 C33.5 34.4 33.5 21.6 40.2 17.6 ' +
            'C46.3 10.6 56.1 10 64 10 ' +
            'C72 10 81.9 10.6 87.8 17.6 ' +
            'C94.6 21.6 94.6 34.4 92.2 40.1 ' +
            'L89.2 35.7 L86.8 40.5 L83.7 35.1 L81.3 39.4 ' +
            'C80 35.1 79.4 33.2 78.8 31.4 ' +
            'C77 28.3 72.7 25.5 67.7 23.9 ' +
            'C66.4 23.5 61.6 23.5 60.4 23.9 ' +
            'C55.4 25.5 51.2 28.3 48.7 31.4 ' +
            'C48.2 33.2 47.6 35.1 46.4 39.4 ' +
            'L44 35.1 L41.5 40.5 L39 35.7 Z', p.hair) +
            stroked('M64 23.6 L64 14.6', 2.7, LINE);                             // 中分缝
          return s;
        }
      },
      {
        id: 'mush', name: '蘑菇头', z: 5,
        draw: function (p) {
          var s = ell(64, 33, 22, 22, p.skin);
          // 蘑菇头：外轮廓与碗形一致，刘海为一条内弧（无锯齿、无中分缝）
          s += shape('M35.9 40.1 C33.5 34.4 33.5 21.6 40.2 17.6 ' +
            'C46.3 10.6 56.1 10 64 10 ' +
            'C72 10 81.9 10.6 87.8 17.6 ' +
            'C94.6 21.6 94.6 34.4 92.2 40.1 ' +
            'C87 25.5 41 25.5 35.9 40.1 Z', p.hair);
          return s;
        }
      }
    ],

    /* ------------------------------------------------ 表情（单选 1 个，绝对坐标） */
    faces: [
      {
        id: 'focus', name: '专注', z: 6,
        draw: function (p) {
          var s = stroked('M50.7 32.2 L58 34.2', 1.8, LINE) +
            stroked('M77.3 32.2 L70 34.2', 1.8, LINE);
          s += dot(55.5, 36.2, 3, LINE) + dot(72.5, 36.2, 3, LINE);
          s += dot(54.7, 35.2, 1.1, '#FFFFFF') + dot(71.7, 35.2, 1.1, '#FFFFFF');
          s += stroked('M61.5 45 L66.5 45', 1.9, LINE);
          return s;
        }
      },
      {
        id: 'grin', name: '傻笑', z: 6,
        draw: function (p) {
          var s = stroked('M51.2 36.9 Q55.5 31.3 59.8 36.9', 2.1, LINE) +
            stroked('M68.2 36.9 Q72.5 31.3 76.8 36.9', 2.1, LINE);
          s += stroked('M59.8 45.5 Q64 49.5 68.2 45.5', 2, LINE);
          s += dot(52.5, 40.2, 3, p.blush) + dot(75.5, 40.2, 3, p.blush);
          return s;
        }
      }
    ],

    /* ------------------------------------------------ 身体套装（单选 1 套 = 5 件整体替换） */
    bodies: [
      {
        id: 'jacket', name: '衬衫·外套·长裤',
        legL: {
          z: 1,
          draw: function (p) {
            return limb('M58 92 L56.5 112', 14, p.pants) + rrect(46, 112.5, 18, 11, 5.5, p.shoe);
          }
        },
        legR: {
          z: 1,
          draw: function (p) {
            return limb('M70 92 L71.5 112', 14, p.pants) + rrect(64, 112.5, 18, 11, 5.5, p.shoe);
          }
        },
        torso: {
          z: 3,
          draw: function (p) {
            return shape('M58 47 L70 47 L70 58 L58 58 Z', p.skinS) +              // 脖子（12 宽）
              shape('M52 62 L76 62 L76 88 L52 88 Z', p.shirt) +                   // 衬衫
              // 外套：斜肩（肩点 44/84@68 → 颈侧 57/71@58）
              shape('M44 68 C48.5 60.5 53 58 57 58 L71 58 ' +
                'C75 58 79.5 60.5 84 68 L86 90 C74 94 54 94 42 90 Z', p.jacket) +
              shape('M58 63 L70 63 L64 74 Z', p.shirt) +                          // V 领露衬衫
              shape('M57 57.5 L64 61.5 L71 57.5 L71 61 L64 65.5 L57 61 Z',        // 衬衫领
                '#F7F1E8') +
              stroked('M64 74 L64 88', 2, p.jacketD);                             // 门襟
          }
        },
        armL: {
          z: 4,
          draw: function (p) {
            return limb('M47 65 L42.5 76', 8.5, p.jacketD) +
              limb('M42.5 76 L41 87', 7, p.skin) + circ(40.5, 89.5, 4.3, p.skin);
          }
        },
        armR: {
          z: 4,
          draw: function (p) {
            return limb('M81 65 L85.5 76', 8.5, p.jacketD) +
              limb('M85.5 76 L87 87', 7, p.skin) + circ(87.5, 89.5, 4.3, p.skin);
          }
        }
      },
      {
        id: 'tee', name: 'T恤·短裤',
        legL: {
          z: 1,
          draw: function (p) {
            return limb('M58 92 L56.5 104', 14, p.shorts) +                       // 短裤
              limb('M56.5 104 L56 112', 9, p.skin) +                              // 小腿
              rrect(46.5, 107.5, 16, 8, 4, p.sock) +
              rrect(46, 112.5, 18, 11, 5.5, p.shoe);
          }
        },
        legR: {
          z: 1,
          draw: function (p) {
            return limb('M70 92 L71.5 104', 14, p.shorts) +
              limb('M71.5 104 L72 112', 9, p.skin) +
              rrect(65.5, 107.5, 16, 8, 4, p.sock) +
              rrect(64, 112.5, 18, 11, 5.5, p.shoe);
          }
        },
        torso: {
          z: 3,
          draw: function (p) {
            return shape('M58 47 L70 47 L70 58 L58 58 Z', p.skinS) +
              shape('M50 60 C54 57.5 74 57.5 78 60 L80 88 C71 91.5 57 91.5 48 88 Z', p.tee) +
              shape('M56.5 57.5 C58.5 61.5 69.5 61.5 71.5 57.5 ' +                // 白色圆领
                'C73.5 60 72.5 63 70 64.3 C66.3 65.8 61.7 65.8 58 64.3 ' +
                'C55.5 63 54.5 60 56.5 57.5 Z', '#F7F1E8');
          }
        },
        armL: {
          z: 4,
          draw: function (p) {
            return limb('M47 65 L42.5 76', 8.5, p.teeD) +
              limb('M42.5 76 L41 87', 7, p.skin) + circ(40.5, 89.5, 4.3, p.skin);
          }
        },
        armR: {
          z: 4,
          draw: function (p) {
            return limb('M81 65 L85.5 76', 8.5, p.teeD) +
              limb('M85.5 76 L87 87', 7, p.skin) + circ(87.5, 89.5, 4.3, p.skin);
          }
        }
      }
    ],

    /* ------------------------------------------------ 挂件（跨分类复选，分类内单选） */
    attachments: [
      {
        id: 'cap_baseball', name: '棒球帽', cat: '帽子', slot: 'head', offset: [0, 0], z: 7.5,
        draw: function (p) {
          return shape('M-19 3 C-19 -7.5 -9.5 -12.5 0 -12.5 C9.5 -12.5 19 -7.5 19 3 Z', p.cap) +
            ell(0, 3, 27.5, 4.2, p.capD) +
            circ(0, -12.5, 2.4, p.capD, 2);
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
        id: 'cape_travel', name: '旅行披风', cat: '披风', slot: 'back', offset: [0, 0], z: 0.5,
        draw: function (p) {
          return shape('M-19 -12 C-30 -4 -30 10 -24 16 C-10 10 10 10 24 16 ' +
            'C30 10 30 -4 19 -12 Z', p.cape) +
            stroked('M-24 14 L-19 20', 2, p.capeD) +
            stroked('M24 14 L19 20', 2, p.capeD);
        }
      },
      {
        id: 'sword_wood', name: '木剑', cat: '武器', slot: 'hand_r', offset: [0, 0], z: 6,
        /* 局部原点 = 右手；旋转 28° 让剑尖指向外上，避开头部 */
        draw: function (p) {
          return '<g transform="rotate(28)">' +
            stroked('M0 8 L0 -5', 3.4, '#6B4A2F') +                              // 剑柄
            shape('M-5.5 -6.5 L5.5 -6.5 L5.5 -3 L-5.5 -3 Z', p.jacketD) +        // 护手
            shape('M0 -33 L4 -27 L4 -4 L-4 -4 L-4 -27 Z', p.jacket) +            // 剑身
            stroked('M0 -26 L0 -6', 1.6, p.jacketD) +                            // 剑脊
            '</g>';
        }
      }
    ]
  };

  global.registerCharacter(P);
})(typeof window !== 'undefined' ? window : globalThis);
/*__CHARFORGE_EDITS__*/registerEdits("boy",{"boy|head:bowl":"<ellipse cx=\"64\" cy=\"33\" rx=\"22\" ry=\"22\" fill=\"#F7C49B\"/><path fill=\"#966E67\" d=\"M35.9 40.1C33.5 34.4 35.3 19.52 42.98 13.71C53.52 5.88 56.1 10 64 10C72 10 66.64 2.97 86 13.02C94.04 18.41 94.6 34.4 92.2 40.1L89.2 35.7L86.8 40.5L83.7 35.1L81.3 39.4C80 35.1 79.4 33.2 78.8 31.4C77 28.3 72.7 25.5 67.7 23.9C66.4 23.5 61.6 23.5 60.4 23.9C55.4 25.5 51.2 28.3 48.7 31.4C48.2 33.2 47.6 35.1 46.4 39.4L44 35.1L41.5 40.5L39 35.7Z\"/><path fill=\"none\" stroke=\"#4A3B42\" stroke-width=\"1\" stroke-linecap=\"round\" stroke-linejoin=\"round\" d=\"M64.28 22.07L64 12.1\"/>"});
