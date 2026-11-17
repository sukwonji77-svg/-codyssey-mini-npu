
import time


def mac(pattern, filter_data):
    score = 0

    for i in range(len(pattern)):
        for j in range(len(pattern[i])):
            score += pattern[i][j] * filter_data[i][j]

    return score

def normalize_label(label):
    if label == "+" or label.lower() == "cross":
        return "Cross"
    elif label.lower() == "x":
        return "X"
    else:
        raise ValueError("알 수 없는 라벨")


def validate_matrix(matrix, size):
    if not isinstance(matrix, list) or len(matrix) != size:
        return False

    for row in matrix:
        if not isinstance(row, list) or len(row) != size:
            return False
        for value in row:
            if type(value) not in (int, float):
                return False

    return True


def analyze_json():
    import json

    with open("data.json", encoding="utf-8") as file:
        data = json.load(file)

    filters = data["filters"]
    patterns = data["patterns"]

    total = 0
    passed = 0
    failures = []

    for key, case in patterns.items():
        total += 1

        try:
            parts = key.split("_")
            size = int(parts[1])
            filter_key = f"size_{size}"

            selected = filters[filter_key]

            cross_filter = selected["cross"]
            x_filter = selected["x"]
            pattern = case["input"]

            if not all([
                validate_matrix(pattern, size),
                validate_matrix(cross_filter, size),
                validate_matrix(x_filter, size)
            ]):
                raise ValueError("패턴 또는 필터 크기/값 오류")

            expected = normalize_label(case["expected"])

            score_cross, score_x, result = classify(
                pattern, cross_filter, x_filter
            )

            if result == "A":
                result = "Cross"
            elif result == "B":
                result = "X"
            else:
                result = "UNDECIDED"

            status = "PASS" if result == expected else "FAIL"

            print(f"\n--- {key} ---")
            print(f"Cross 점수: {score_cross:.16f}")
            print(f"X 점수: {score_x:.16f}")
            print(f"판정: {result} | expected: {expected} | {status}")

            if status == "PASS":
                passed += 1
            else:
                failures.append((key, f"판정 {result}, 예상 {expected}"))

        except (KeyError, ValueError, TypeError, IndexError) as error:
            failures.append((key, str(error)))
            print(f"\n--- {key} ---")
            print(f"FAIL: {error}")

    performance_analysis(filters)
    print("\n=== 결과 요약 ===")
    print(f"총 테스트: {total}개")
    print(f"통과: {passed}개")
    print(f"실패: {len(failures)}개")

    for key, reason in failures:
        print(f"- {key}: {reason}")


def read_matrix(name):
    while True:
        print(f"\n{name} 입력 (3줄, 숫자 3개씩)")
        matrix = []

        try:
            for i in range(3):
                line = input(f"{i + 1}행: ")
                row = [float(x) for x in line.split()]

                if len(row) != 3:
                    raise ValueError("숫자 3개가 필요합니다.")

                matrix.append(row)

            return matrix

        except ValueError:
            print("입력 형식 오류: 각 줄에 숫자 3개를 공백으로 구분해 입력하세요.")
            print("처음부터 다시 입력합니다.")


def classify(pattern, filter_a, filter_b):
    score_a = mac(pattern, filter_a)
    score_b = mac(pattern, filter_b)

    epsilon = 1e-9

    if abs(score_a - score_b) < epsilon:
        result = "판정 불가"
    elif score_a > score_b:
        result = "A"
    else:
        result = "B"

    return score_a, score_b, result


def performance_analysis(filters=None):
    print("\n=== 성능 분석 (100회 평균) ===")
    print("크기       평균 시간(ms)     연산 횟수")
    print("------------------------------------")

    for size in [3, 5, 13, 25]:
        if size == 3:
            pattern = [
                [0, 1, 0],
                [1, 1, 1],
                [0, 1, 0]
            ]
            filter_data = pattern

        else:
            filter_data = filters[f"size_{size}"]["cross"]
            pattern = filter_data

        repeat = 100

        start = time.perf_counter()

        for _ in range(repeat):
            mac(pattern, filter_data)

        elapsed = time.perf_counter() - start
        average_ms = elapsed * 1000 / repeat

        print(
            f"{size}x{size:<5} "
            f"{average_ms:>12.6f} "
            f"{size * size:>12}"
        )


def main():
    print("=== Mini NPU Simulator ===")
    print("1. 사용자 입력 (3x3)")
    print("2. data.json 분석 (다음 단계에서 구현)")

    mode = input("모드 선택: ")

    if mode == "1":
        filter_a = read_matrix("필터 A")
        filter_b = read_matrix("필터 B")

        print("\n필터 A와 B 저장 완료")

        pattern = read_matrix("입력 패턴")

        start = time.perf_counter()

        score_a, score_b, result = classify(
            pattern, filter_a, filter_b
        )

        elapsed = (time.perf_counter() - start) * 1000

        print("\n=== MAC 결과 ===")
        print("A 점수:", score_a)
        print("B 점수:", score_b)
        print("판정:", result)
        print(f"연산 시간: {elapsed:.6f} ms")
        performance_analysis({
    "size_5": {"cross": [[1.0] * 5 for _ in range(5)]},
    "size_13": {"cross": [[1.0] * 13 for _ in range(13)]},
    "size_25": {"cross": [[1.0] * 25 for _ in range(25)]}
})

    elif mode == "2":
        analyze_json()

    else:
        print("잘못된 모드입니다.")


if __name__ == "__main__":
    main()

