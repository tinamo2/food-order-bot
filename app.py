import streamlit as st
import json
import os

# پیکربندی صفحه
st.set_page_config(page_title="ربات سفارش غذا 🍔", layout="centered")

# استایل فونت فارسی و راست‌چین
st.markdown("""
<style>
@font-face {
    font-family: 'Vazir';
    src: url('https://cdn.fontcdn.ir/Font/Persian/Vazir/Vazir.woff2') format('woff2');
}
html, body, [class*="css"] {
    font-family: 'Vazir', sans-serif;
    direction: rtl;
    text-align: right;
}
</style>
""", unsafe_allow_html=True)

st.title(" ربات سفارش غذا")

# بارگذاری منو
try:
    with open("menu.json", "r", encoding="utf-8") as f:
        menu = json.load(f)
except FileNotFoundError:
    st.error("فایل منو پیدا نشد!")
    st.stop()

# مقداردهی اولیه
if "cart" not in st.session_state:
    st.session_state.cart = []
if "search" not in st.session_state:
    st.session_state.search = ""
if "show_popup" not in st.session_state:
    st.session_state.show_popup = False

# جستجو
st.text_input("🔍 جستجوی غذا:", key="search")

# انتخاب دسته‌بندی
categories = list(menu.keys())
selected_category = st.selectbox(" انتخاب دسته‌بندی:", categories)

# فیلتر آیتم‌ها با جستجو
search_term = st.session_state.search.strip()
filtered_items = []
for category, items in menu.items():
    for item in items:
        if search_term in item['name']:
            item_with_category = item.copy()
            item_with_category['category'] = category
            filtered_items.append(item_with_category)

if not search_term:
    filtered_items = menu[selected_category]

# نمایش آیتم‌ها
for item in filtered_items:
    with st.container():
        col1, col2 = st.columns([1, 2])
        with col1:
            if os.path.exists(item["image"]):
                st.image(item["image"], width=130)
            else:
                st.warning("تصویر یافت نشد")
        with col2:
            st.markdown(f"### {item['name']}")
            st.markdown(f" قیمت: {item['price']} تومان")
            st.markdown(f" {item['description']}")

            eat_type = st.radio(
                f"نوع سفارش برای {item['name']}:",
                ["صرف در رستوران", "بسته‌بندی بیرون‌بر"],
                key=f"eat_type_{item['name']}"
            )

            custom = st.multiselect(
                f"ترکیبات برای {item['name']}:",
                options=item.get("options", []),
                default=item.get("options", []),
                key=f"opts_{item['name']}"
            )

            if st.button(f"➕ افزودن {item['name']} به سبد خرید", key=f"add_{item['name']}"):
                selected_item = item.copy()
                selected_item["custom"] = custom
                selected_item["eat_type"] = eat_type
                st.session_state.cart.append(selected_item)
                st.success(f"{item['name']} اضافه شد ✅")
        st.markdown("---")

# نمایش سبد خرید
if st.session_state.cart:
    st.subheader("🛒 سبد خرید شما:")
    total = 0
    for i, item in enumerate(st.session_state.cart):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"• {item['name']} ({item['eat_type']}) - {item['price']} تومان")
            if item.get("custom"):
                st.markdown(f"  ترکیبات: {', '.join(item['custom'])}")
        with col2:
            if st.button("❌ حذف", key=f"remove_{i}"):
                del st.session_state.cart[i]
                st.experimental_rerun()
        total += int(item['price'])

    st.markdown(f"###  مجموع: {total} تومان")

    if st.button("✅ ثبت نهایی سفارش"):
        st.session_state.show_popup = True

# فرم پاپ‌آپ شماره تماس
if st.session_state.show_popup:
    with st.expander("📱 ورود شماره تماس برای ادامه سفارش", expanded=True):
        phone = st.text_input("شماره تماس:", max_chars=11, key="user_phone")
        if st.button(" ادامه به پرداخت"):
            if phone == "" or len(phone) < 10:
                st.error("شماره تماس معتبر نیست!")
            else:
                try:
                    with open("orders.txt", "a", encoding="utf-8") as f:
                        f.write("سفارش جدید:\n")
                        f.write(f"شماره تماس: {phone}\n")
                        for item in st.session_state.cart:
                            f.write(f"{item['name']} - {item['price']} تومان - {item['eat_type']}\n")
                            if item.get("custom"):
                                f.write(f"  ترکیبات: {', '.join(item['custom'])}\n")
                        f.write(f"جمع کل: {total} تومان\n-----\n")
                except:
                    st.error("خطا در ذخیره سفارش!")
                st.success("✅ سفارش ثبت شد! در حال انتقال به درگاه پرداخت ...")
                st.markdown(f"[ پرداخت آنلاین تستی](https://zarinpal.com/pg/StartPay/FakeAuthority)", unsafe_allow_html=True)
                st.session_state.cart = []
                st.session_state.show_popup = False
