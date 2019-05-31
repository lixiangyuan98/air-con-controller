    // vue.config.js
module.exports = {
    // 修改的配置
    baseUrl: '/',
    devServer: {
        proxy: {
            '': {
                target: 'http://118.89.219.248:8080',
                changeOrigin: true,
                pathRewrite: {}
            }
        }
    }
}
    // .env.development
      //VUE_APP_BASE_API= /api
