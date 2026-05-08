# Marabou MNIST 강건성 검증 (Robustness Verification)

[Marabou](https://github.com/NeuralNetworkVerification/Marabou)를 활용하여 신경망의 국소적 강건성(local robustness)을 공식 검증(formal verification)합니다.

이 프로젝트는 MNIST 데이터셋으로 학습된 소형 완전연결 신경망(Fully-Connected Network)이 L-inf 섭동 공격(perturbation attacks)에 대해 얼마나 안전한지 SMT 기반 완전 검증(complete verification)을 통해 확인합니다.

## 기능 요약

- MNIST용 784→64→32→10 FC 네트워크 학습 (테스트 정확도 >97%)
- 학습된 모델을 ONNX 형식으로 변환 및 추출
- Marabou를 사용한 공식 검증 수행: *"어떤 입력 x가 숫자 d로 분류될 때, ||x'−x||∞ ≤ ε를 만족하는 모든 입력 x' 역시 숫자 d로 분류되는가?"*

## 설치 및 준비

### 1. 소스에서 Marabou 빌드

Marabou는 소스 코드를 통해 직접 빌드해야 합니다. (기존 파이썬 3.8-3.11용 pip 휠이 제공되지만, 모든 파이썬 버전을 지원하기 위해 소스 빌드를 권장합니다).

```bash
# 빌드 의존성 설치 (macOS)
brew install cmake boost wget

# 클론 및 빌드
git clone https://github.com/NeuralNetworkVerification/Marabou/
cd Marabou
mkdir build && cd build
cmake ../ -DCMAKE_POLICY_VERSION_MINIMUM=3.5
cmake --build . -j 4
```

### 2. PYTHONPATH 설정

```bash
export PYTHONPATH=/path/to/Marabou:$PYTHONPATH
```

`/path/to/Marabou` 부분을 실제 Marabou가 클론된 디렉토리 경로로 변경해주세요. (예: `.../Marabou_src`)

### 3. Python 의존성 설치

```bash
pip install -r requirements.txt
```

## 실행 방법

### 1단계 — 모델 학습

```bash
python train_model.py
```

MNIST FC 네트워크를 5 에폭 동안 학습하고 다음 파일들을 저장합니다:
- `models/mnist_fc.onnx` — 추출된 ONNX 모델
- `models/sample_inputs.npy` — 올바르게 분류된 테스트 샘플들
- `models/sample_labels.npy` — 샘플에 해당하는 라벨(정답)

### 2단계 — Marabou 검증 실행

```bash
python test.py
```

선택적 인자(Optional arguments):

| 플래그 | 기본값 | 설명 |
|------|---------|-------------|
| `--epsilon` | `0.01` | L-inf 섭동 반경 (perturbation radius) |
| `--sample-idx` | `0` | 검증할 샘플의 인덱스 |
| `--timeout` | `300` | 검증 제한 시간 (초 단위) |

사용자 지정 epsilon 예시:

```bash
python test.py --epsilon 0.005 --sample-idx 3
```

## 예상 출력 예시

```
============================================================
Marabou Local Robustness Verification
============================================================
  Model:       models/mnist_fc.onnx
  Sample idx:  0  (true label: 7)
  Epsilon:     0.01  (L-inf ball)
  Timeout:     300s
============================================================
...
RESULT
============================================================
  Verification time: 12.43s
  Verdict:  UNSAT
  Meaning:  The network always predicts class 7
            for all inputs within the L-inf ball of radius 0.01.
```

## 저장소 구조

```
.
├── README.md               # 영문 설명서
├── README_ko.md            # 한국어 설명서
├── requirements.txt
├── train_model.py          # MNIST FC 학습 및 ONNX 추출
├── test.py                 # Marabou 검증 스크립트
├── exploration.md          # Marabou 기본 리소스 분석
├── report.txt              # 영문 분석 보고서
├── report_ko.txt           # 한국어 분석 보고서
└── models/
    ├── mnist_fc.onnx           # 학습된 모델 (생성됨)
    ├── sample_inputs.npy       # 테스트 샘플 (생성됨)
    └── sample_labels.npy       # 샘플 라벨 (생성됨)
```
