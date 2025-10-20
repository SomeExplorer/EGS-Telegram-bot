from enum import Enum
from typing import Union

from pydantic import BaseModel, Field, AnyUrl, AwareDatetime, FutureDatetime


class ImageType(str, Enum):
    OFFER_IMAGE_WIDE = "OfferImageWide"
    OFFER_IMAGE_TALL = "OfferImageTall"
    THUMBNAIL = "Thumbnail"
    HERO_CAROUSEL_VIDEO = "heroCarouselVideo"
    FEATURED_MEDIA = "featuredMedia"
    GALLERY_IMAGE = "GalleryImage"


class KeyImageSchema(BaseModel):
    type: ImageType
    url: AnyUrl


class SellerSchema(BaseModel):
    id: str
    name: str


class PageSchema(BaseModel):
    page_slug: str = Field(alias="pageSlug")
    page_type: str = Field(alias="pageType")


class TotalPriceSchema(BaseModel):
    discount_price: int = Field(ge=0, alias="discountPrice")
    original_price: int = Field(gt=0, alias="originalPrice")
    discount: int = Field(ge=0)


class PriceSchema(BaseModel):
    total_price: TotalPriceSchema = Field(alias="totalPrice")


class DiscountSettingSchema(BaseModel):
    discount_type: str = Field(alias="discountType")
    discount_percentage: int = Field(ge=0, alias="discountPercentage")


class PromotionalOfferSchema(BaseModel):
    start_date: AwareDatetime = Field(alias="startDate")
    end_date: Union[AwareDatetime, FutureDatetime] = Field(alias="endDate")
    discount_setting: DiscountSettingSchema = Field(alias="discountSetting")


class PromotionalOffersListSchema(BaseModel):
    promotional_offers: list[PromotionalOfferSchema] = Field(alias="promotionalOffers")


class PromotionsSchema(BaseModel):
    promotional_offers: list[PromotionalOffersListSchema] | None = Field(
        alias="promotionalOffers"
    )
    upcoming_promotional_offers: list[PromotionalOffersListSchema] | None = Field(
        alias="upcomingPromotionalOffers"
    )


class GameInfoSchema(BaseModel):
    title: str
    id: str
    description: str
    key_images: list[KeyImageSchema] = Field(alias="keyImages")
    seller: SellerSchema
    offer_mappings: list[PageSchema] = Field(alias="offerMappings")
    price: PriceSchema
    promotions: PromotionsSchema | None
