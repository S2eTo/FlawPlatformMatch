class SelectOption {
    /**
     * 目标值
     * @type {string}
     */
    value = ""

    /**
     * 显示对象列表
     * @type {[Element]}
     */
    show = []

    /**
     * 隐藏对象列表
     * @type {[Element]}
     */
    hide = []

    /**
     *
     * @param value {String}                目标值
     * @param show {[Element]}              显示对象对标
     * @param hide {[Element]}              隐藏对象列表
     * @param callback {Function|null}      回调函数
     */
    constructor(value, show, hide, callback = null) {
        this.value = value;
        this.show = show;
        this.hide = hide;
    }
}

class SelectChangeDisplay {

    /**
     * 监听对象
     * @type {HTMLSelectElement}
     */
    el = null

    /**
     * 选项配置
     * @type {[SelectOption]}
     */
    option = []

    /**
     * 根据下拉选择框不同的值，显示或隐藏固定内容。
     *
     * @param el {HTMLSelectElement}                监听目标
     * @param option {...SelectOption}              显示/隐藏配置参数、不限数参数
     * @constructor
     */
    constructor(el, ...option) {
        this.el = el;
        this.option = option;

        // 初始化一次
        this.__onchange();
        let self = this;
        el.onchange = function () {self.__onchange()};
    }

    /**
     *
     * @param self
     * @returns {(function())|*}
     * @private
     */
    __onchange(self = null) {
        let selected_value = this.el[this.el.selectedIndex].value.toString();
        let option = this.option.filter(function (value, index, array) {
            if (value.value.toString() === selected_value) return value
        })[0]

        option.show.forEach(function (value, index, array) {
            value.hidden = false;
        })

        option.hide.forEach(function (value, index, array) {
            value.hidden = true;
        })
    }
}

