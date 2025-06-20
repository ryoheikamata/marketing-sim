"""ROAS計算のテストスクリプト"""

# テストケース
test_cases = [
    {"売上": 500, "広告費": 150, "期待ROAS": 333},  # 500/150*100 = 333.33
    {"売上": 1000, "広告費": 200, "期待ROAS": 500}, # 1000/200*100 = 500
    {"売上": 300, "広告費": 300, "期待ROAS": 100},  # 300/300*100 = 100
    {"売上": 800, "広告費": 160, "期待ROAS": 500},  # 800/160*100 = 500
]

print("ROAS計算テスト")
print("=" * 50)
print("ROAS = (売上 ÷ 広告費) × 100")
print("=" * 50)

for i, case in enumerate(test_cases, 1):
    売上 = case["売上"]
    広告費 = case["広告費"]
    期待値 = case["期待ROAS"]
    
    # ROAS計算
    roas = (売上 / 広告費 * 100) if 広告費 > 0 else 0
    roas_rounded = round(roas, 0)
    
    print(f"\nテストケース {i}:")
    print(f"  売上: {売上}万円")
    print(f"  広告費: {広告費}万円")
    print(f"  計算式: {売上} ÷ {広告費} × 100 = {roas:.2f}")
    print(f"  ROAS: {roas_rounded}% (期待値: {期待値}%)")
    print(f"  結果: {'✓ OK' if roas_rounded == 期待値 else '✗ NG'}")

# 広告費率によるROAS変動シミュレーション
print("\n" + "=" * 50)
print("広告費率によるROAS変動シミュレーション")
print("=" * 50)

売上 = 1000
for 広告費率 in [10, 20, 30, 40, 50]:
    広告費 = 売上 * 広告費率 / 100
    roas = (売上 / 広告費 * 100) if 広告費 > 0 else 0
    print(f"広告費率 {広告費率}%: 売上{売上}万円、広告費{広告費:.0f}万円 → ROAS {roas:.0f}%")

print("\n結論: ROASは広告費率が高いほど低くなります（反比例の関係）")