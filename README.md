<div align="center">

# 🎬 ViewFlex+

<img width="300px" src="README_img/logo.png" alt="ViewFlex+ 로고" />

### 내 맘에 쏙! 똑똑한 영화 추천 서비스

</div>

---

## ⭐ 주요 기능
### 1. 실시간 인기 영화 랭킹 기능

- **Redis Sorted Set 기반 스코어링**
  - 가중치: 조회(1), 좋아요(5), 리뷰(3), 높은평점(4), 중간평점(2), 낮은평점(1)

- **시간대별 랭킹 관리**
  - 만료: 일간(24시간), 주간(7일), 전체(무기한)
  - 키 구조: `trending:movies:daily`, `trending:movies:weekly`, `trending:movies:all`

- **성능 최적화**
  - 캐시: Django 캐싱으로 5분간 결과 저장
  - 동시성: Redis 원자적 연산(`ZINCRBY`)으로 안전한 데이터 처리