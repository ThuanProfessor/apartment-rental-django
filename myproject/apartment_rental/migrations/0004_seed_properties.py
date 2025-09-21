from django.db import migrations, transaction, models
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db.utils import IntegrityError, DataError
from decimal import Decimal
from django.utils import timezone


def field_names(model):
    return {f.name for f in model._meta.get_fields() if getattr(f, 'concrete', False) and not f.many_to_many}


def forwards(apps, schema_editor):
    # Use historical models
    app_label, model_name = settings.AUTH_USER_MODEL.split('.')
    User = apps.get_model(app_label, model_name)
    Property = apps.get_model("apartment_rental", "Property")

    # Optional PropertyImage
    try:
        PropertyImage = apps.get_model("apartment_rental", "PropertyImage")
    except LookupError:
        PropertyImage = None

    prop_fields = field_names(Property)

    # Helpers to respect model constraints
    def sanitize_kwargs(kwargs):
        data = dict(kwargs)
        for name, value in list(data.items()):
            try:
                f = Property._meta.get_field(name)
            except Exception:
                continue
            # truncate long strings
            max_len = getattr(f, 'max_length', None)
            if max_len and isinstance(value, str):
                data[name] = value[:max_len]
            # choices enforcement
            choices = getattr(f, 'choices', None)
            if choices:
                valid = {c[0] for c in choices}
                if data.get(name) not in valid:
                    data[name] = next(iter(valid)) if valid else data.get(name)
            # decimal normalization
            if isinstance(f, models.DecimalField) and isinstance(value, (int, float)):
                data[name] = Decimal(str(value))
        return data

    def fill_required_scalars(kwargs):
        data = dict(kwargs)
        for f in Property._meta.get_fields():
            if getattr(f, 'auto_created', False) or getattr(f, 'primary_key', False):
                continue
            # For ForeignKey required without default, if missing -> skip (return None)
            if isinstance(f, models.ForeignKey):
                if not getattr(f, 'null', True) and f.name not in data:
                    return None
                continue
            if getattr(f, 'concrete', False) and not getattr(f, 'null', True) and f.name not in data:
                # No default provided on field? Provide sensible fallback
                if isinstance(f, models.CharField):
                    data[f.name] = ''
                elif isinstance(f, models.TextField):
                    data[f.name] = ''
                elif isinstance(f, models.BooleanField):
                    data[f.name] = False
                elif isinstance(f, models.IntegerField):
                    data[f.name] = 0
                elif isinstance(f, models.FloatField):
                    data[f.name] = 0.0
                elif isinstance(f, models.DecimalField):
                    data[f.name] = Decimal('0')
                elif isinstance(f, models.DateField):
                    data[f.name] = timezone.now().date()
                elif isinstance(f, models.DateTimeField):
                    data[f.name] = timezone.now()
                else:
                    # leave as-is; DB may have default
                    pass
        return data

    # Ensure a landlord owner account
    landlord, _ = User.objects.get_or_create(
        username="landlord1",
        defaults={
            "email": "landlord1@example.com",
            "first_name": "Lan",
            "last_name": "Dlrd",
            "password": make_password("landlord123"),
        },
    )
    if hasattr(landlord, "user_type") and getattr(landlord, "user_type", None) != "landlord":
        landlord.user_type = "landlord"
        landlord.save(update_fields=["user_type"])

    # Sample data (concise but diverse); will be expanded with small variants
    blocks = [
        dict(title="Căn hộ studio trung tâm Quận 1", property_type="apartment", address="45 Lê Lai", district="Quận 1", city="Ho Chi Minh", area=28, price=9000000, bedrooms=0, bathrooms=1, status="available", description="Studio nội thất cơ bản, gần công viên 23/9."),
        dict(title="Phòng trọ mới, gần Bùi Viện", property_type="room", address="120 Bùi Viện", district="Quận 1", city="Ho Chi Minh", area=16, price=4500000, bedrooms=0, bathrooms=1, status="available", description="Phòng có cửa sổ, vệ sinh riêng, giờ giấc tự do."),
        dict(title="Căn hộ 1PN view Bitexco", property_type="apartment", address="12 Tôn Đức Thắng", district="Quận 1", city="Ho Chi Minh", area=45, price=15000000, bedrooms=1, bathrooms=1, status="available", description="Nội thất cao cấp, gần bến Bạch Đằng."),
        dict(title="Phòng trọ Quận 3 gần CV Lê Văn Tám", property_type="room", address="25 Hai Bà Trưng", district="Quận 3", city="Ho Chi Minh", area=18, price=5000000, bedrooms=0, bathrooms=1, status="available", description="Máy lạnh, giờ giấc tự do."),
        dict(title="Căn hộ 2PN Trần Quốc Thảo", property_type="apartment", address="180 Trần Quốc Thảo", district="Quận 3", city="Ho Chi Minh", area=65, price=18000000, bedrooms=2, bathrooms=1, status="available", description="Full nội thất, ban công thoáng."),
        dict(title="Phòng trọ Phú Mỹ Hưng", property_type="room", address="R15-3 Hưng Gia", district="Quận 7", city="Ho Chi Minh", area=20, price=6000000, bedrooms=0, bathrooms=1, status="available", description="Gần Crescent Mall, an ninh."),
        dict(title="Căn hộ Sky Garden 2PN", property_type="apartment", address="Sky Garden, Tân Phong", district="Quận 7", city="Ho Chi Minh", area=72, price=16000000, bedrooms=2, bathrooms=2, status="available", description="Hồ bơi, gym, công viên."),
        dict(title="Phòng trọ Điện Biên Phủ", property_type="room", address="521 Điện Biên Phủ", district="Bình Thạnh", city="Ho Chi Minh", area=14, price=3500000, bedrooms=0, bathrooms=1, status="available", description="Gần Hutech, thoáng mát."),
        dict(title="Căn hộ Landmark 81 1PN", property_type="apartment", address="Vinhomes Central Park", district="Bình Thạnh", city="Ho Chi Minh", area=52, price=22000000, bedrooms=1, bathrooms=1, status="available", description="View sông, tiện ích 5*."),
        dict(title="Phòng trọ Linh Trung ĐHQG", property_type="room", address="12 Đường 6, Linh Trung", district="Thủ Đức", city="Ho Chi Minh", area=18, price=3000000, bedrooms=0, bathrooms=1, status="available", description="Gần KTX ĐHQG, giờ tự do."),
        dict(title="Căn hộ Opal Boulevard 2PN", property_type="apartment", address="Phạm Văn Đồng", district="Thủ Đức", city="Ho Chi Minh", area=68, price=13000000, bedrooms=2, bathrooms=2, status="available", description="Ban công rộng, nội thất mới."),
        dict(title="Phòng trọ gần sân bay", property_type="room", address="8/5 Trường Sơn", district="Tân Bình", city="Ho Chi Minh", area=15, price=3800000, bedrooms=0, bathrooms=1, status="available", description="Phù hợp nhân viên sân bay."),
        dict(title="Căn hộ 1PN Cộng Hòa", property_type="apartment", address="385 Cộng Hòa", district="Tân Bình", city="Ho Chi Minh", area=48, price=10000000, bedrooms=1, bathrooms=1, status="available", description="Gần ETown, đủ nội thất."),
        dict(title="Phòng trọ Huỳnh Văn Bánh", property_type="room", address="121 Huỳnh Văn Bánh", district="Phú Nhuận", city="Ho Chi Minh", area=18, price=4200000, bedrooms=0, bathrooms=1, status="available", description="Gần Trường Sa, ẩm thực phong phú."),
        dict(title="Căn hộ Phan Xích Long 2PN", property_type="apartment", address="Phan Xích Long", district="Phú Nhuận", city="Ho Chi Minh", area=65, price=16000000, bedrooms=2, bathrooms=2, status="available", description="Khu sầm uất, tiện ích đủ."),
        dict(title="Phòng trọ Quang Trung", property_type="room", address="600 Quang Trung", district="Gò Vấp", city="Ho Chi Minh", area=16, price=3000000, bedrooms=0, bathrooms=1, status="available", description="Gần Emart, có máy lạnh."),
        dict(title="Nhà Cityland Garden Hills", property_type="house", address="Cityland Garden Hills", district="Gò Vấp", city="Ho Chi Minh", area=180, price=32000000, bedrooms=5, bathrooms=4, status="available", description="Khu cao cấp, an ninh tốt."),
        dict(title="Studio Phố Cổ", property_type="apartment", address="18 Hàng Bạc", district="Hoàn Kiếm", city="Ha Noi", area=30, price=10000000, bedrooms=0, bathrooms=1, status="available", description="Giữa Phố Cổ, full nội thất."),
        dict(title="Phòng trọ Tràng Tiền", property_type="room", address="22 Tràng Tiền", district="Hoàn Kiếm", city="Ha Noi", area=15, price=4500000, bedrooms=0, bathrooms=1, status="available", description="Gần Nhà Hát Lớn, sạch sẽ."),
        dict(title="Nhà Hàng Bè 3PN", property_type="house", address="6/3 Hàng Bè", district="Hoàn Kiếm", city="Ha Noi", area=110, price=25000000, bedrooms=3, bathrooms=2, status="available", description="Phong cách Indochine."),
        dict(title="Căn hộ 1PN Kim Mã", property_type="apartment", address="95 Kim Mã", district="Ba Đình", city="Ha Noi", area=48, price=12000000, bedrooms=1, bathrooms=1, status="available", description="Gần Lotte, máy giặt riêng."),
        dict(title="Phòng trọ Đội Cấn", property_type="room", address="182 Đội Cấn", district="Ba Đình", city="Ha Noi", area=17, price=3500000, bedrooms=0, bathrooms=1, status="available", description="Có gác lửng, gần chợ."),
        dict(title="Căn hộ 2PN Liễu Giai", property_type="apartment", address="Liễu Giai", district="Ba Đình", city="Ha Noi", area=70, price=16000000, bedrooms=2, bathrooms=2, status="available", description="Gần công viên Thủ Lệ."),
        dict(title="Phòng trọ Trần Thái Tông", property_type="room", address="25 Trần Thái Tông", district="Cầu Giấy", city="Ha Noi", area=16, price=3200000, bedrooms=0, bathrooms=1, status="available", description="Gần CV Cầu Giấy."),
        dict(title="Căn hộ 2PN Duy Tân", property_type="apartment", address="66 Duy Tân", district="Cầu Giấy", city="Ha Noi", area=68, price=14000000, bedrooms=2, bathrooms=1, status="available", description="Khu văn phòng, tiện đi lại."),
        dict(title="Nhà Nghĩa Tân 4PN", property_type="house", address="12/5 Nghĩa Tân", district="Cầu Giấy", city="Ha Noi", area=150, price=23000000, bedrooms=4, bathrooms=3, status="available", description="Gần chợ/trường học."),
        dict(title="Phòng trọ Bạch Mai", property_type="room", address="220 Bạch Mai", district="Hai Bà Trưng", city="Ha Noi", area=14, price=2800000, bedrooms=0, bathrooms=1, status="available", description="Gần Bách Khoa."),
        dict(title="Times City 1PN", property_type="apartment", address="458 Minh Khai", district="Hai Bà Trưng", city="Ha Noi", area=55, price=13000000, bedrooms=1, bathrooms=1, status="available", description="Tiện ích nội khu đủ."),
        dict(title="Times City 2PN", property_type="apartment", address="458 Minh Khai", district="Hai Bà Trưng", city="Ha Noi", area=70, price=17000000, bedrooms=2, bathrooms=2, status="available", description="Phù hợp gia đình trẻ."),
    ]

    variants = [
        dict(price_delta=0, area_delta=0, suffix=""),
        dict(price_delta=200000, area_delta=2, suffix=" (ban công)"),
        dict(price_delta=-200000, area_delta=-2, suffix=" (giá tốt)"),
    ]

    created = 0
    with transaction.atomic():
        for base in blocks:
            for var in variants:
                if created >= 40:
                    break
                data = base.copy()
                data["title"] = (base["title"] + var["suffix"])[:200]
                data["price"] = max(0, base["price"] + var["price_delta"])
                data["area"] = max(0, base["area"] + var["area_delta"])

                if "owner" in prop_fields:
                    data["owner"] = landlord

                safe_kwargs = {k: v for k, v in data.items() if k in prop_fields}
                safe_kwargs = sanitize_kwargs(safe_kwargs)
                safe_kwargs = fill_required_scalars(safe_kwargs)
                if safe_kwargs is None:
                    continue  # missing required FK

                try:
                    obj = Property.objects.create(**safe_kwargs)
                except (IntegrityError, DataError):
                    continue  # skip problematic row

                created += 1

                # Attach images if model exists
                if PropertyImage:
                    pi_fields = field_names(PropertyImage)
                    urls = [
                        "https://images.unsplash.com/photo-1600585154526-990dced4db0d",
                        "https://images.unsplash.com/photo-1560448075-bb4caa6c0f11",
                        "https://images.unsplash.com/photo-1505691938895-1758d7feb511",
                    ]
                    for u in urls:
                        img_kwargs = {}
                        if "property" in pi_fields:
                            img_kwargs["property"] = obj
                        if "image" in pi_fields:
                            img_kwargs["image"] = u
                        if img_kwargs:
                            try:
                                PropertyImage.objects.create(**img_kwargs)
                            except Exception:
                                pass


def backwards(apps, schema_editor):
    Property = apps.get_model("apartment_rental", "Property")
    Property.objects.filter(title__startswith="Căn hộ studio trung tâm Quận 1").delete()
    Property.objects.filter(title__startswith="Phòng trọ mới, gần Bùi Viện").delete()
    Property.objects.filter(title__startswith="Căn hộ 1PN view Bitexco").delete()
    Property.objects.filter(title__startswith="Phòng trọ Quận 3 gần CV Lê Văn Tám").delete()
    Property.objects.filter(title__startswith="Căn hộ 2PN Trần Quốc Thảo").delete()
    Property.objects.filter(title__startswith="Phòng trọ Phú Mỹ Hưng").delete()
    Property.objects.filter(title__startswith="Căn hộ Sky Garden 2PN").delete()
    Property.objects.filter(title__startswith="Phòng trọ Điện Biên Phủ").delete()
    Property.objects.filter(title__startswith="Căn hộ Landmark 81 1PN").delete()
    Property.objects.filter(title__startswith="Phòng trọ Linh Trung ĐHQG").delete()
    Property.objects.filter(title__startswith="Căn hộ Opal Boulevard 2PN").delete()
    Property.objects.filter(title__startswith="Phòng trọ gần sân bay").delete()
    Property.objects.filter(title__startswith="Căn hộ 1PN Cộng Hòa").delete()
    Property.objects.filter(title__startswith="Phòng trọ Huỳnh Văn Bánh").delete()
    Property.objects.filter(title__startswith="Căn hộ Phan Xích Long 2PN").delete()
    Property.objects.filter(title__startswith="Phòng trọ Quang Trung").delete()
    Property.objects.filter(title__startswith="Nhà Cityland Garden Hills").delete()
    Property.objects.filter(title__startswith="Studio Phố Cổ").delete()
    Property.objects.filter(title__startswith="Phòng trọ Tràng Tiền").delete()
    Property.objects.filter(title__startswith="Nhà Hàng Bè 3PN").delete()
    Property.objects.filter(title__startswith="Căn hộ 1PN Kim Mã").delete()
    Property.objects.filter(title__startswith="Phòng trọ Đội Cấn").delete()
    Property.objects.filter(title__startswith="Căn hộ 2PN Liễu Giai").delete()
    Property.objects.filter(title__startswith="Phòng trọ Trần Thái Tông").delete()
    Property.objects.filter(title__startswith="Căn hộ 2PN Duy Tân").delete()
    Property.objects.filter(title__startswith="Nhà Nghĩa Tân 4PN").delete()
    Property.objects.filter(title__startswith="Phòng trọ Bạch Mai").delete()
    Property.objects.filter(title__startswith="Times City 1PN").delete()
    Property.objects.filter(title__startswith="Times City 2PN").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("apartment_rental", "0003_favorite"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]