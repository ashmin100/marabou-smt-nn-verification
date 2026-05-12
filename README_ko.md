# Marabou를 활용한 신경망 검증

> SMT 기반 완전 검증(Formal Verification)으로 MNIST 분류기의 국소적 강건성(Local Robustness)을 수학적으로 증명합니다 — L∞ 섭동 반경 내의 어떤 적대적 입력도 예측 클래스를 바꿀 수 없음을 보장합니다.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![Framework](https://img.shields.io/badge/Verifier-Marabou%202.0-orange)
![Model](https://img.shields.io/badge/Model-ONNX%20opset%2011-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 개요

이 프로젝트는 [Marabou](https://github.com/NeuralNetworkVerification/Marabou) (Katz et al., CAV 2019)를 사용해 MNIST로 학습된 소형 완전연결 신경망의 **국소적 강건성**을 공식 검증합니다.

FGSM, PGD 같은 기울기 기반 공격은 적대적 예제를 *탐색*할 뿐이지만, Marabou는 **완전한 증명**을 제공합니다. UNSAT 결과는 섭동 반경 내의 *어떤* 입력도 예측 클래스를 바꿀 수 없음을 수학적으로 보장합니다.

```
∀x' s.t. ‖x' − x‖_∞ ≤ ε  ⟹  argmax f(x') = d
```

---

## 주요 실험 결과

물리적 픽셀 경계 클리핑 적용 후, ε = 0.01 ~ 0.20 전 구간 스윕:

| ε (정규화) | ε (실제 픽셀값, ÷255) | 판정 | 소요 시간 |
|:---:|:---:|:---:|---:|
| 0.01 | ~0.8/255 | **UNSAT** | 0.51s |
| 0.05 | ~4.0/255 | **UNSAT** | 0.47s |
| 0.10 | ~8.1/255 | **UNSAT** | 0.95s |
| 0.15 | ~12.1/255 | **UNSAT** | 12.80s |
| 0.18 | ~14.6/255 | **UNSAT** | 138.20s |
| 0.20 | ~16.2/255 | **UNSAT** | 300.60s |

> **핵심 발견:** 물리적 픽셀 경계 클리핑 적용 시, ε=0.12 검증 시간이 248s → 6s로 **40배 단축**되었으며 ε=0.15에서의 False SAT도 해소됨. 전 구간 모두 UNSAT(완전 강건) 판정.

---

## 모델 아키텍처

```
MNIST 이미지 (28×28)
       │
       ▼
  Flatten → [784]
       │
  Linear(784→64) + ReLU
       │
  Linear(64→32)  + ReLU
       │
  Linear(32→10)
       │
  argmax → 예측 숫자
```

**테스트 정확도:** ~97.5%  |  **포맷:** ONNX opset 11  |  **파라미터 수:** ~55,000개

---

## 설치 방법

### 1. Marabou 소스 빌드

```bash
# macOS 의존성 설치
brew install cmake boost wget

# 클론 및 빌드
git clone https://github.com/NeuralNetworkVerification/Marabou/
cd Marabou && mkdir build && cd build
cmake ../ -DCMAKE_POLICY_VERSION_MINIMUM=3.5
cmake --build . -j 4
```

### 2. PYTHONPATH 설정

```bash
export PYTHONPATH=/path/to/Marabou:$PYTHONPATH
```

`/path/to/Marabou`를 실제 클론된 Marabou 디렉토리 경로로 교체하세요.

### 3. Python 의존성 설치

```bash
pip install -r requirements.txt
```

---

## 실행 방법

**1단계 — 모델 학습 및 추출**

```bash
python train_model.py
```

생성 파일: `models/mnist_fc.onnx`, `models/sample_inputs.npy`, `models/sample_labels.npy`

**2단계 — 검증 실행**

```bash
python test.py [--epsilon FLOAT] [--sample-idx INT] [--timeout INT]
```

| 플래그 | 기본값 | 설명 |
|---|:---:|---|
| `--epsilon` | `0.01` | L∞ 섭동 반경 (정규화 공간) |
| `--sample-idx` | `0` | 검증할 테스트 샘플 인덱스 |
| `--timeout` | `300` | 솔버 타임아웃 (초) |

**예시**

```bash
python test.py --epsilon 0.05 --sample-idx 2
python test.py --epsilon 0.15 --timeout 600
```

**3단계 — 전 구간 실험 스윕**

```bash
python run_experiments.py   # ε = 0.01 → 0.20 자동 실행, results/results.md에 저장
```

**결과 시각화**

```bash
python visualize_results.py  # 검증 시간 vs epsilon 차트 생성
```

---

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

[1/4] Loading ONNX model into Marabou...
[2/4] Setting input constraints (L-inf ball, epsilon=0.01)...
[3/4] Setting output constraints (violation: any class j≠7 wins)...
[4/4] Running Marabou verification...

============================================================
RESULT
============================================================
  Verification time: 0.51s
  Verdict:  UNSAT
  Meaning:  The network always predicts class 7
            for all inputs within the L-inf ball of radius 0.01.
============================================================
```

---

## 저장소 구조

```
.
├── README.md
├── README_ko.md
├── requirements.txt
├── train_model.py          # MNIST FC 학습 + ONNX 추출
├── test.py                 # Marabou 검증 쿼리 (메인 진입점)
├── run_experiments.py      # 전 구간 epsilon 스윕 (0.01 → 0.20)
├── visualize_results.py    # 검증 시간 vs epsilon 차트 생성
├── exploration_report.md   # Marabou 기본 리소스 분석 (Problem 1)
├── report.md               # 영문 분석 보고서
├── report_ko.md            # 한국어 분석 보고서
├── models/
│   ├── mnist_fc.onnx       # 학습된 모델 (train_model.py 실행 시 생성)
│   ├── sample_inputs.npy   # 테스트 샘플 (생성됨)
│   └── sample_labels.npy   # 라벨 (생성됨)
└── results/
    ├── results.md          # 전 구간 실험 결과 표
    └── verification_results.png
```

---

## 참고 문헌

- Katz, G. et al. *The Marabou Framework for Verification and Analysis of Deep Neural Networks.* CAV 2019.
- Szegedy, C. et al. *Intriguing Properties of Neural Networks.* ICLR 2014.
