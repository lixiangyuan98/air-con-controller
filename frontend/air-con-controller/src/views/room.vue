<template>
  <div id="roomaircontrol">
    <div class="roomtop">
      <p>{{room.id}}</p>
        <button class="returnbtn" v-on:click="check_out"><i class="fa fa-times-rectangle"></i></button>
    </div>
    <div class="roommain">
      <div class="roomcontain roomcontain_2">
          <div class="roomcontainer">
            <p>
              当前费用
              {{ room.cost }}
            </p>
          </div>
          <div class="roomcontainer">
            <p>
              当前温度
              {{ room.temperature }}
            </p>
          </div>
          <div class="roomcontainer">
            <p>
              当前风速
              {{ room.wind }}
            </p>
          </div>
      </div>
      <div class="roomcontain roomcontain_2">
          <div class="roomcontainer">
              <button class="roomcontainerleft" v-on:click="on">
                <p>开</p>
              </button>
              <button class="roomcontainerright" v-on:click="off">
                <p>关</p>
              </button>
          </div>
          <div class="roomcontainer">
            <button class="roomcontainerleft" v-on:click="temper_add">
              <p>升高温度</p>
            </button>
            <button class="roomcontainerright" v-on:click="temper_min">
              <p>降低温度</p>
            </button>
          </div>
          <div class="roomcontainer">
            <button class="roomcontainerleft" v-on:click="wind_add">
              <p>加大风速</p>
            </button>
            <button class="roomcontainerright" v-on:click="wind_min">
              <p>调小风速</p>
            </button>
          </div>
      </div>
    </div>
  </div>
</template>

<style>
  html, body, #roomaircontrol{
    width: 100%;
    height:100%;
    margin: 0;
    padding: 0;
    background-color: #173446;
    color: #598DAC;
  }
  .roomtop{
    text-align: center;
    width:100%;
    height:79px;
    background-color: #09212F;
    color: #7296AC;
    border-bottom: 1px solid #1A2B36;
  }
  .returnbtn{
    background-color: #09212F;
    position: absolute;
    top: 0;
    right: 0;
    height: 79px;
    width:79px;
    font-size: 28px;
  }
  .returnbtn:hover{
    transition: all 0.7s;
    background-color: #010101;
  }
  .roommain{
    height: calc(100% - 80px);
    width: 100%;
  }
  .roomcontain{
    height: 100%;
    width: calc(50% - 1px);
    display: flex;
    flex-direction:column;
    float: left;
    border-right: 1px solid #598DAC;
  }
  .roomcontain:nth-of-type(2){
    border-right: 0px;
    border-left: 1px solid #598DAC;
  }
  .roomcontainer{
    height: 33.3%;
    width: 100%;
    text-align: center;
  }
  .roomcontainer p,.roomtop p{
    line-height: 2em;
    font-size: 2em;
    position: relative;
    top: calc(50% - 1em);
    margin: 0;
  }
  .roomcontainerleft, .roomcontainerright {
    height: 100%;
    width: 50%;
    float: left;
  }
  button{
    margin: 0;
    padding: 0;
    border: 0;
    outline: none;
    background-color: #173446;
    color: #598DAC;
  }
  button:hover{
    transition: all 0.7s;
    background-color: #1A2B36;
  }
</style>

<script>
// @ is an alias to /src

export default {
  data() {
    return {
      room:{
        id: '312C',//传参
        cost: 0,
        temperature: 0,//传参
        wind: 0,
      }
    }
  },
  methods: {
    check_out: function(){
      this.$router.push("/");
    },
    on: function(){
      this.room.cost=0;
    },
    off: function(){
      this.room.cost=0;
      this.room.wind=0;
    },
    temper_add: function(){
      this.room.temperature=this.room.temperature+1;
    },
    temper_min: function(){
      this.room.temperature=this.room.temperature-1;
    },
    wind_add: function(){
      this.room.wind=this.room.wind+1;
    },
    wind_min: function(){
      this.room.wind=this.room.wind-1;
    },
  }
}
</script>
