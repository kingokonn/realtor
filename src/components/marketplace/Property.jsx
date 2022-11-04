import React, {useState} from "react";
import PropTypes from "prop-types";
import {Badge, Button, Card, Col, FloatingLabel, Form, Stack} from "react-bootstrap";
import {microAlgosToString, truncateAddress} from "../../utils/conversions";
import Identicon from "../utils/Identicon";


const Property = ({address, property, buyProperty, deleteProperty, likeProperty, sellProperty}) => {
    const {name, image, description, location, sellprice, sale, likes, appId, owner} = property;
   

    return (
        <Col key={appId}>
            <Card className="h-100">
                <Card.Header>
                    <Stack direction="horizontal" gap={2}>
                        <span className="font-monospace text-secondary">{truncateAddress(owner)}</span>
                        <Identicon size={28} address={owner}/>

                    </Stack>
                </Card.Header>
                <div className="ratio ratio-4x3">
                    <img src={image} alt={name} style={{objectFit: "cover"}}/>
                </div>
                <Card.Body className="d-flex flex-column text-center">
                    <Card.Text className="flex-grow-1">{description}</Card.Text>
                    <Card.Text className="flex-grow-1">{location}</Card.Text>
                    <Card.Text className="flex-grow-1">{likes} Likes</Card.Text>
                    <Form className="d-flex align-content-stretch flex-row gap-2">
                        
                        {property.owner !== address && sale === 1 ? (
                        <Button
                            variant="outline-dark"
                            onClick={() => buyProperty(property)}
                            className="w-75 py-3"
                        >
                            Buy for {microAlgosToString(sellprice)} ALGO
                        </Button>
                        ):(
                            <Card.Text className="flex-grow-1">{property.owner !== address ? "SOLD" : ""}</Card.Text>
                        )
                        }
                        {property.owner === address &&
                            <Button
                                variant="outline-danger"
                                onClick={() => deleteProperty(property)}
                                className="btn"
                            >
                                <i className="bi bi-trash"></i>
                            </Button>
                        }

                        </Form>


             {property.owner !== address &&
                            <Button
                                variant="outline-danger mt-2"
                                onClick={() => likeProperty(property)}
                                className="btn"
                            >
                               Like Property
                            </Button>
                        }



                   {property.owner === address && sale === 0 &&
                            <Button
                                variant="outline-danger"
                                onClick={() => sellProperty(property)}
                                className="btn"
                            >
                                Sell
                            </Button>
                        }

                </Card.Body>
            </Card>
        </Col>
    );
};

Property.propTypes = {
    address: PropTypes.string.isRequired,
    property: PropTypes.instanceOf(Object).isRequired,
    buyProperty: PropTypes.func.isRequired,
    likeProperty: PropTypes.func.isRequired,
    sellProperty: PropTypes.func.isRequired,
    deleteProperty: PropTypes.func.isRequired
};

export default Property;
