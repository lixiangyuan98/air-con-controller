<template>
  <div id="serverpage">
    <div v-if="poweron" class="servercontainer">
      <div class="servercontain">
        设置最高温度：
        <input v-if="!startup" class="serverinput" v-model="highest_temper">
        <span v-if="startup">{{ highest_temper }}</span>
      </div>
      <div class="servercontain">
        设置最低温度：
        <input v-if="!startup" class="serverinput" v-model="lowest_temper">
        <span v-if="startup">{{ lowest_temper }}</span>
      </div>
      <div class="servercontain">
        设低风速费率：
        <input v-if="!startup" class="serverinput" v-model="low_speed_fee">
        <span v-if="startup">{{ low_speed_fee }}</span>
      </div>
      <div class="servercontain">
        设中风速费率：
        <input v-if="!startup" class="serverinput" v-model="middle_speed_fee">
        <span v-if="startup">{{ middle_speed_fee }}</span>
      </div>
      <div class="servercontain">
        设高风速费率：
        <input v-if="!startup" class="serverinput" v-model="high_speed_fee">
        <span v-if="startup">{{ high_speed_fee }}</span>
      </div>
      <div class="servercontain">
        设置默认温度：
        <input v-if="!startup" class="serverinput" v-model="default_temper">
        <span v-if="startup">{{ default_temper }}</span>
      </div>
      <div class="servercontain">
        设置默认风速：
        <input v-if="!startup" class="serverinput" v-model="default_speed">
        <span v-if="startup">{{ default_speed }}</span>
      </div>
      <div class="servercontain">
        设置默认模式：
        <input v-if="!startup" class="serverinput" v-model="mode">
        <span v-if="startup">{{ mode }}</span>
      </div>
    </div>
    <div class="serverfoot">
      <button class="serverbtn" v-on:click="power_on"><i class="fa fa-power-off"></i></button>
      <button class="serverbtn" v-on:click="start_up"><i class="fa fa-play"></i></button>
      <button class="serverbtn" v-on:click="changerole"><i class="fa fa-times-rectangle"></i></button>
    </div>
  </div>
</template>

<style>
  html,body,#serverpage {
    width: 100%;
    height: 100%;
    margin: 0;
    background-color: #173446;
    color: #598DAC;
  }

  button {
    margin: 0;
    padding: 0;
    border: 0;
    outline: none;
    background-color: #173446;
    color: #598DAC;
  }

  .serverbtn {
    background-color: none;
    margin: 0 100px;
    height: 80px;
    width: 80px;
    font-size: 28px;
  }

  .serverbtn:hover {
    transition: all 0.7s;
    color: #010101;
  }

  .servercontainer {
    padding: 40px 0 0 0;
  }

  .servercontain {
    margin: 24px 0;
    font-size: 24px;
    text-align: center;
    line-height: 48px;
  }

  .serverfoot {
    display: flex;
    justify-content: center;
    padding-top: 40px;
  }

  .serverinput {
    font-size: 24px;
    line-height: 28px;
    color: #7296AC;
    background: none;
    border: none;
    margin: 0;
    border-bottom: 2px solid #7296AC;
  }
</style>

<script>
// @ is an alias to /src
export default {
  data() {
    return {
      highest_temper: '',
      lowest_temper: '',
      low_speed_fee: '',
      middle_speed_fee: '',
      high_speed_fee: '',
      default_temper: '',
      default_speed: '',
      mode: '',
      startup: false,
      poweron: false,
    }
  },
  methods: {
    power_on: function() {
      //power_on
      this.poweron = true;
    },
    start_up: function() {
      //start_up
      this.startup = true;
    },
    changerole: function() {
      //start_up
      this.$router.push("/");
    },
  }
}
</script>
