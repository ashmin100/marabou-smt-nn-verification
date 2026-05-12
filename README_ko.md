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

2단계 실험: (1) 100개 테스트 이미지를 ε=0.05로 스캔해 SAT 샘플 탐색, (2) 3개 대표 샘플에 대해 ε ∈ [0.01, 0.20] 전 구간 스윕.

**샘플별 강건성 경계:**

| 샘플 | 실제 레이블 | ε* (경계) | 인증 범위 | 적대적 클래스 |
|:----:|:----------:|:---------:|:---------:|:------------:|
| idx=0 | 7 | > 0.20 | ≥ 0.20 (전 구간) | — |
| idx=8 | 5 | ≈ 0.03 | 0.02까지 | 6 |
| idx=33 | 4 | ≈ 0.05 | 0.04까지 | 0 |

**선택된 ε에서의 런타임 비교:**

| ε (정규화) | ε (÷255) | idx=0 | idx=8 | idx=33 |
|:----------:|:--------:|:-----:|:-----:|:------:|
| 0.03 | ~2.4/255 | UNSAT  0.5s | **SAT  0.5s** | UNSAT  0.5s |
| 0.05 | ~4.0/255 | UNSAT  0.5s | SAT  0.8s | **SAT  0.5s** |
| 0.15 | ~12.1/255 | UNSAT  14.3s | SAT  1.1s | SAT  0.5s |
| 0.20 | ~16.2/255 | UNSAT  300.5s | SAT  0.6s | SAT  0.5s |

> **핵심 발견:** SAT 쿼리는 목격자(witness) 하나를 발견하는 즉시 종료되어 거의 항상 1초 미만입니다. 반면 UNSAT는 2^96개 분기를 모두 탐색해야 하므로 최대 300초까지 소요됩니다. 이 비대칭성은 NP-난이도 문제의 완전 검증에 내재된 특성입니다.
>
> **False SAT 수정:** 물리적 픽셀 경계 클리핑(`[-0.4242, 2.8215]`) 없이 실험 시 ε=0.12 런타임이 6s → 248s로 폭증하고 ε=0.15에서 허위 SAT가 발생했습니다.

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

**2단계 — 단일 검증 쿼리 실행**

```bash
python test.py [--epsilon FLOAT] [--sample-idx INT] [--timeout INT]
```

| 플래그 | 기본값 | 설명 |
|--------|:------:|------|
| `--epsilon` | `0.01` | L∞ 섭동 반경 (정규화 공간) |
| `--sample-idx` | `0` | 검증할 테스트 샘플 인덱스 |
| `--timeout` | `300` | 솔버 타임아웃 (초) |

```bash
python test.py --epsilon 0.05 --sample-idx 8    # SAT — 적대적 예제 발견
python test.py --epsilon 0.15 --sample-idx 0    # UNSAT — 강건성 인증
```

**3단계 — 2단계 실험 스윕 실행**

```bash
python run_experiments.py
# Phase 1: 0~99번 샘플을 ε=0.05로 스캔, SAT 샘플 탐색
# Phase 2: 기준선 + SAT 샘플에 대해 ε=0.01→0.20 스윕
# 출력: results/results.md
```

**4단계 — 결과 시각화**

```bash
python visualize_results.py
# 3개 샘플 런타임 막대 차트 + 판정 히트맵 생성
# 출력: results/verification_results.png
```

---

## 예상 출력 예시 (SAT 케이스)

```
============================================================
Marabou Local Robustness Verification
============================================================
  Sample idx:  8  (true label: 5)
  Epsilon:     0.03  (L-inf ball)
============================================================
  Verdict:  SAT (counterexample found)
  Meaning:  An adversarial input exists within the L-inf ball.

  Adversarial class predicted: 6  (true: 5)
  Max perturbation (L-inf):    0.029997
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
├── run_experiments.py      # 2단계 실험 (샘플 스캔 + ε 스윕)
├── visualize_results.py    # 런타임 막대 차트 + 판정 히트맵
├── exploration_report.md   # Marabou 기본 리소스 분석 (Problem 1)
├── report.md               # 영문 분석 보고서
├── report_ko.md            # 한국어 분석 보고서
├── models/
│   ├── mnist_fc.onnx       # 학습된 모델 (train_model.py 실행 시 생성)
│   ├── sample_inputs.npy   # 테스트 샘플 (생성됨)
│   └── sample_labels.npy   # 라벨 (생성됨)
└── results/
    ├── results.md                  # 전 구간 실험 결과 표
    └── verification_results.png   # 런타임 + 판정 시각화
```

---

## 참고 문헌

- Katz, G. et al. *The Marabou Framework for Verification and Analysis of Deep Neural Networks.* CAV 2019.
- Szegedy, C. et al. *Intriguing Properties of Neural Networks.* ICLR 2014.
