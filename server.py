from sanic import Sanic
from sanic.response import json

from chartbox.slide import slide_cnt

# 初始化 Sanic
app = Sanic(__name__)

app.static("/", "./templates/index.html", name="index")
app.static("/bar_test", "./templates/bar_test.html", name="bar_test")
app.static("/slide", "./templates/slide.html", name="slide")


@app.route("/bar_test_data", methods=["GET"])
async def draw_bar_chart(request):
    from chartbox.test001 import bar_test
    c = bar_test()
    return json(c.dump_options_with_quotes())


@app.route("/slide_cnt_data", methods=["GET"])
async def slide_cnt_data(request):
    c = slide_cnt()
    return json(c.dump_options_with_quotes())


if __name__ == '__main__':
    # mf
    app.run(host="0.0.0.0", port=17312, debug=True)
