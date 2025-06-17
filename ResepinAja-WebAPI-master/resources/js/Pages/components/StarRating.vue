<template>
  <div class="star-rating" v-for="index in 5" :key="index">
    <!-- Full star -->
    <i 
      v-if="shouldShowFullStar(index)" 
      class="bi bi-star-fill text-warning" :class="customs"
    ></i>
      
    <!-- Half star -->
    <i 
      v-else-if="shouldShowHalfStar(index)" 
      class="bi bi-star-half text-warning" :class="customs"
    ></i>
      
    <!-- Empty star -->
    <i 
      v-else 
      class="bi bi-star text-warning" :class="customs"
    ></i>
  </div>
</template>

<script>
export default {
  props: {
    rating: {
      type: Number,
      required: true,
      validator: value => value >= 0 && value <= 5
    },
    customs:{
      type: String,
      default: ''
    }
  },
  computed: {
    normalizedRating() {
      const decimal = this.rating % 1;
      if (decimal < 0.5) {
        return Math.floor(this.rating);
      }
      return Math.floor(this.rating) + 0.5;
    }
  },
  methods: {
    shouldShowFullStar(index) {
      return index <= Math.floor(this.normalizedRating);
    },
    shouldShowHalfStar(index) {
      const hasHalfStar = this.normalizedRating % 1 !== 0;
      return hasHalfStar && index === Math.ceil(this.normalizedRating);
    }
  }
};
</script>

<style scoped>
.star-rating {
  display: inline-flex;
  gap: 2px;
}
.text-warning {
  color: #ffc107;
}
</style>