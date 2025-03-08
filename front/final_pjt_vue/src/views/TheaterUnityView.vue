<!-- UnityView.vue -->
<template>
  <div class="unity-container">
    <iframe 
      src="/unity/index.html" 
      class="unity-frame"
      frameborder="0" 
      id="unityFrame">
    </iframe>

    <div class="seat-layout">
      <div class="screen-indicator"></div>
      <div v-for="row in rows" :key="row" class="seat-row">
        <div class="row-label">{{ String.fromCharCode(65 + row) }}</div>
        <div class="seats">
          <button 
            v-for="col in columns" 
            :key="col"
            class="seat-button"
            :class="{ 
              'selected': selectedRow === row && selectedCol === col,
              'occupied': isOccupied(row, col)
            }"
            @click="selectSeatByClick(row, col)"
          >
            {{ String(col).padStart(2, '0') }}
          </button>
        </div>
      </div>
    </div>

    <div class="controls">
      <div class="control-row">
        <div class="height-selection">
          <label>키 설정:</label>
          <select v-model="selectedHeight" @change="selectSeat">
            <option v-for="height in heights" :key="height" :value="height">
              {{ height }}cm
            </option>
          </select>
        </div>
        <button @click="playTrailer" class="trailer-button">
          {{ isPlaying ? '일시정지' : '예고편 재생' }}
        </button>
      </div>
    </div>

    <div class="popcorn-animation" v-if="showPopcorn">
      <div class="popcorn-container">
        <span class="main-popcorn">🍿</span>
        <div class="popcorn-pieces">
          <span class="piece" v-for="n in 12" :key="n">🍿</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: "TheaterUnityView",
  props: {
    movieId: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      selectedRow: 3,
      selectedCol: 6,
      selectedHeight: 170,
      isPlaying: false,
      rows: Array.from({ length: 5 }, (_, i) => i),
      columns: Array.from({ length: 15 }, (_, i) => i + 1),
      heights: Array.from({ length: 9 }, (_, i) => 150 + (i * 5)),
      movieMap: {
        '9999999': '위키드',
        '9999998': '모아나2',
        '9999997': '히든페이스',
        '9999996': '나히아.mp4',
        '9999995': '글래디에이터2',
        '9999994': '청설',
        '9999993': '베놈',
        '9999992': '사흘',
        '9999991': '아마존활명수',
        '9999990': '컨택트'
      },
      showPopcorn: true,
    };
  },
  async mounted() {
    window.addEventListener("message", this.receiveSeatSelection);
    setTimeout(() => {
      this.showPopcorn = false;
    }, 4000);
  },
  methods: {
    selectSeat() {
      const unityFrame = document.getElementById("unityFrame").contentWindow;
      
      if (unityFrame) {
        const seatData = {
          row: this.selectedRow,
          col: this.selectedCol,
          height: this.selectedHeight,
          type: 'seat'
        };
        
        const origin = window.location.origin;
        unityFrame.postMessage(seatData, origin);
        console.log('좌석 선택:', seatData);
      }
    },

    playTrailer() {
      const unityFrame = document.getElementById("unityFrame").contentWindow;
      
      if (unityFrame) {
        if (this.isPlaying) {
          const pauseData = {
            type: 'pauseTrailer'
          };
          unityFrame.postMessage(pauseData, window.location.origin);
        } else {
          const fullscreenData = {
            type: 'setFullscreen'
          };
          unityFrame.postMessage(fullscreenData, window.location.origin);

          setTimeout(() => {
            const videoName = this.movieMap[this.movieId] || 'default';
            const trailerData = {
              type: 'trailer',
              videoPath: videoName
            };
            unityFrame.postMessage(trailerData, window.location.origin);
          }, 100);
        }
        this.isPlaying = !this.isPlaying;
      }
    },

    stopTrailer() {
    const unityFrame = document.getElementById("unityFrame").contentWindow;
    
      if (unityFrame) {
        const stopData = {
          type: 'stopTrailer'
        };
        
        const origin = window.location.origin;
        unityFrame.postMessage(stopData, origin);
      }
    },

    receiveSeatSelection(event) {
      if (event.origin !== window.location.origin) return;
      
      const seatData = event.data;
      console.log("Unity에서 받은 좌석 데이터:", seatData);
      
      if (seatData.row !== undefined && seatData.col !== undefined) {
        this.selectedRow = seatData.row;
        this.selectedCol = seatData.col;
        if (seatData.height !== undefined) {
          this.selectedHeight = seatData.height;
        }
      }
    },

    selectSeatByClick(row, col) {
      if (this.isOccupied(row, col)) return;
      
      this.selectedRow = row;
      this.selectedCol = col;
      this.selectSeat();
    },

    isOccupied(row, col) {
      const occupiedSeats = [
      ];
      return occupiedSeats.some(seat => seat.row === row && seat.col === col);
    }
  },
  beforeDestroy() {
    window.removeEventListener("message", this.receiveSeatSelection);
  }
};
</script>

<style scoped>
.unity-container {
  width: 100vw;
  height: 100vh;
  top: 0;
  left: 0;
  position: fixed;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-height: 100vh;
  background-color: #000;
  animation: fadeInUnity 1s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: opacity, transform;
}

@keyframes fadeInUnity {
  0% {
    opacity: 0;
    transform: scale(1.02);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

.unity-frame {
  width: 100%;
  aspect-ratio: 16/9;
  position: relative;
  z-index: 1;
  margin-top: -1.5%;
  margin-right: 33%;
  animation: frameAppear 0.8s cubic-bezier(0.4, 0, 0.2, 1) 0.2s both;
}

@keyframes frameAppear {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.controls {
  position: relative;
  z-index: 2;
  margin-top: -27%;
  margin-right: -68%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  background-color: #000000;
  padding: 15px 25px;
  border-radius: 8px;
  width: fit-content;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
}

.control-row {
  display: flex;
  align-items: center;
  gap: 20px;
}

.height-selection {
  display: flex;
  align-items: center;
  gap: 10px;
}

select {
  padding: 5px;
  border-radius: 4px;
  border: 1px solid #ccc;
  background-color: white;
  color: #333;
}

label {
  font-weight: bold;
  color: white;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
}

.button-group {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.select-button {
  padding: 8px 16px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: bold;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.select-button:hover {
  background-color: #45a049;
  transform: translateY(-1px);
}

.trailer-button {
  padding: 8px 16px;
  background-color: #2195f3dc;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: bold;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.trailer-button:hover {
  background-color: #1976D2;
  transform: translateY(-1px);
}

.popcorn-animation {
  position: fixed;
  top: 40%;
  left: 35%;
  transform: translate(-50%, -50%);
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  pointer-events: none;
  animation: fadeOut 0.5s ease-out 3s forwards;
}

.popcorn-container {
  position: relative;
  width: 100px;
  height: 100px;
}

.main-popcorn {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 13rem;
  animation: riseAndPop 1.2s ease-out forwards;
}

.popcorn-pieces {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 100%;
  height: 100%;
  transform: translate(-50%, -50%);
}

.popcorn-pieces .piece {
  position: absolute;
  font-size: 3rem;
  opacity: 0;
}

/* 각 팝콘의 초기 위치를 원형으로 배치 */
.popcorn-pieces .piece:nth-child(1) { top: 45%; left: 45%; }
.popcorn-pieces .piece:nth-child(2) { top: 45%; left: 48%; }
.popcorn-pieces .piece:nth-child(3) { top: 45%; left: 51%; }
.popcorn-pieces .piece:nth-child(4) { top: 48%; left: 45%; }
.popcorn-pieces .piece:nth-child(5) { top: 48%; left: 48%; }
.popcorn-pieces .piece:nth-child(6) { top: 48%; left: 51%; }
.popcorn-pieces .piece:nth-child(7) { top: 51%; left: 45%; }
.popcorn-pieces .piece:nth-child(8) { top: 51%; left: 48%; }
.popcorn-pieces .piece:nth-child(9) { top: 51%; left: 51%; }
.popcorn-pieces .piece:nth-child(10) { top: 54%; left: 46%; }
.popcorn-pieces .piece:nth-child(11) { top: 54%; left: 49%; }
.popcorn-pieces .piece:nth-child(12) { top: 54%; left: 52%; }

/* 애니메이션 시작점도 수정 */
@keyframes scatter1 { 
  0% { transform: translate(0, 0); opacity: 1; }
  100% { transform: translate(-200px, -300px) rotate(720deg); opacity: 0; }
}

@keyframes scatter2 { 
  0% { transform: translate(0, 0); opacity: 1; }
  100% { transform: translate(-150px, -250px) rotate(720deg); opacity: 0; }
}

@keyframes scatter3 { 
  0% { transform: translate(0, 0); opacity: 1; }
  100% { transform: translate(-100px, 100px) rotate(720deg); opacity: 0; }
}

@keyframes scatter4 { 
  0% { transform: translate(0, 0); opacity: 1; }
  100% { transform: translate(0, -200px) rotate(720deg); opacity: 0; }
}

@keyframes scatter5 { 
  0% { transform: translate(0, 0); opacity: 1; }
  100% { transform: translate(0, 200px) rotate(720deg); opacity: 0; }
}

@keyframes scatter6 { 
  0% { transform: translate(0, 0); opacity: 1; }
  0% { transform: translate(-50%, -50%); opacity: 1; }
  100% { transform: translate(100px, -100px) rotate(720deg); opacity: 0; }
}

@keyframes scatter7 { 
  0% { transform: translate(-50%, -50%); opacity: 1; }
  100% { transform: translate(150px, -150px) rotate(720deg); opacity: 0; }
}

@keyframes scatter8 { 
  0% { transform: translate(-50%, -50%); opacity: 1; }
  100% { transform: translate(150px, 100px) rotate(720deg); opacity: 0; }
}

@keyframes scatter9 { 
  0% { transform: translate(-50%, -50%); opacity: 1; }
  100% { transform: translate(-250px, 0) rotate(720deg); opacity: 0; }
}

@keyframes scatter10 { 
  0% { transform: translate(-50%, -50%); opacity: 1; }
  100% { transform: translate(250px, 0) rotate(720deg); opacity: 0; }
}

@keyframes scatter11 { 
  0% { transform: translate(-50%, -50%); opacity: 1; }
  100% { transform: translate(-150px, 150px) rotate(720deg); opacity: 0; }
}

@keyframes scatter12 { 
  0% { transform: translate(-50%, -50%); opacity: 1; }
  100% { transform: translate(150px, 150px) rotate(720deg); opacity: 0; }
}

/* 각 팝콘에 애니메이션 적용 - 12개 모두 다른 방향으로 수정 */
.popcorn-pieces .piece:nth-child(1) { animation: scatter1 1s ease-out 0.8s forwards; }  /* 왼쪽 위 */
.popcorn-pieces .piece:nth-child(2) { animation: scatter2 1s ease-out 0.85s forwards; }  /* 왼쪽 중간 위 */
.popcorn-pieces .piece:nth-child(3) { animation: scatter3 1s ease-out 0.9s forwards; }  /* 왼쪽 중간 아래 */
.popcorn-pieces .piece:nth-child(4) { animation: scatter4 1s ease-out 0.95s forwards; }  /* 위 */
.popcorn-pieces .piece:nth-child(5) { animation: scatter5 1s ease-out 1s forwards; }  /* 아래 */
.popcorn-pieces .piece:nth-child(6) { animation: scatter6 1s ease-out 1.05s forwards; }  /* 오른쪽 위 */
.popcorn-pieces .piece:nth-child(7) { animation: scatter7 1s ease-out 1.1s forwards; }  /* 오른쪽 중간 위 */
.popcorn-pieces .piece:nth-child(8) { animation: scatter8 1s ease-out 1.15s forwards; }  /* 오른쪽 중간 아래 */
.popcorn-pieces .piece:nth-child(9) { animation: scatter9 1s ease-out 1.2s forwards; }  /* 왼쪽 */
.popcorn-pieces .piece:nth-child(10) { animation: scatter10 1s ease-out 1.25s forwards; }  /* 오른쪽 */
.popcorn-pieces .piece:nth-child(11) { animation: scatter11 1s ease-out 1.3s forwards; }  /* 왼쪽 아래 */
.popcorn-pieces .piece:nth-child(12) { animation: scatter12 1s ease-out 1.35s forwards; }  /* 오른쪽 아래 */

/* 메인 팝콘 애니메이션 수정 */
@keyframes riseAndPop {
  0% { transform: translate(-50%, 200%) scale(1); opacity: 1; }
  60% { transform: translate(-50%, -100%) scale(1.2); opacity: 1; }
  80% { transform: translate(-50%, -120%) scale(1.2); opacity: 1; }
  100% { transform: translate(-50%, -120%) scale(0); opacity: 0; }
}

@keyframes fadeOut {
  to {
    opacity: 0;
    visibility: hidden;
  }
}

.seat-layout {
  position: absolute;
  right: -250px;
  top: 43%;
  margin-right: -1%;
  transform: translateY(-50%);
  background: #000000;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
  z-index: 2;
  animation: slideIn 0.6s cubic-bezier(0.4, 0, 0.2, 1) 0.5s both;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px) translateX(-50%);
  }
  to {
    opacity: 1;
    transform: translateY(-50%) translateX(-50%);
  }
}

.seat-row {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.row-label {
  color: white;
  font-weight: bold;
  margin-right: 15px;
  width: 20px;
}

.seats {
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
}

.seat-button {
  width: 35px;
  height: 35px;
  border: none;
  border-radius: 6px;
  background: #2c3e50;
  color: white;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.seat-button:hover {
  background: #34495e;
  transform: translateY(-2px);
}

.seat-button.selected {
  background: #2196F3;
  box-shadow: 0 0 15px rgba(33, 150, 243, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.seat-button.occupied {
  background: #95a5a6;
  cursor: not-allowed;
}

.screen-indicator {
  width: 80%;
  height: 8px;
  background: linear-gradient(to right, #4a90e2, #63b8ff);
  margin: 15px auto 30px;
  border-radius: 4px;
  position: relative;
}

.screen-indicator::before {
  content: 'SCREEN';
  position: absolute;
  top: -25px;
  left: 50%;
  transform: translateX(-50%);
  color: white;
  font-size: 14px;
  letter-spacing: 2px;
}

</style>