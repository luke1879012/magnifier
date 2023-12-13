from sanic import Sanic
from sanic.response import json

from chartbox.bidp import bidp_api_heart, bidp_api_update
from chartbox.login import login_status
from chartbox.sche import sche_run_time
from chartbox.slide import slide_cnt

# 初始化 Sanic
app = Sanic(__name__)

# 直连文件
# 企业微信认证
app.static("/WW_verify_L8rDvLaOxx6rJ5fJ.txt", "./direct_file/WW_verify_L8rDvLaOxx6rJ5fJ.txt", name="wx_verify")


app.static("/", "./templates/index.html", name="index")
app.static("/static", "./static", name="static_data")
app.static("/bar_test", "./templates/bar_test.html", name="bar_test")
app.static("/slide", "./templates/slide.html", name="slide")
app.static("/login_status", "./templates/slide.html", name="login_status")
app.static("/sche", "./templates/sche_run.html", name="sche")


@app.route("/bar_test_data", methods=["GET"])
async def draw_bar_chart(request):
    from chartbox.test001 import bar_test
    c = bar_test()
    return json(c.dump_options_with_quotes())


@app.route("/slide_cnt_data", methods=["GET"])
async def slide_cnt_data(request):
    c = slide_cnt()
    return json(c.dump_options_with_quotes())


@app.route("/bidp_heart_data", methods=["GET"])
async def bidp_heart_data(request):
    c = bidp_api_heart()
    return json(c.dump_options_with_quotes())


@app.route("/bidp_heart_data_update", methods=["GET"])
async def bidp_heart_data_update(request):
    last_time = request.args.get("last_time")
    # print(last_time)
    if not last_time:
        return json([])
    new_data = bidp_api_update(last_time)
    for i in new_data:
        if i[0] > last_time:
            return json([i])
    return json(new_data)


@app.route("/login_status_data", methods=["GET"])
async def login_status_data(request):
    c = login_status()
    return json(c.dump_options_with_quotes())


@app.route("/sche_status_data", methods=["GET"])
async def sche_status_data(request):
    c = sche_run_time()
    return json(c.dump_options_with_quotes())


if __name__ == '__main__':
    # mf
    app.run(host="0.0.0.0", port=17312, debug=True)
